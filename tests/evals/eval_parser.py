"""
Parser evaluation: how many fields does the LLM extract correctly?

    python -m tests.evals.eval_parser               # local report
    python -m tests.evals.eval_parser --langsmith   # also save as a LangSmith experiment
"""
import json
import sys
from pathlib import Path

from backend.agents.query_parser import parse_query
from backend.guardrails.input_checks import InputRejected, check_input

DATASET = json.loads((Path(__file__).parent / "parser_dataset.json").read_text(encoding="utf-8"))
DATASET_NAME = "tripmate-parser"


def run_parser(inputs: dict) -> dict:
    try:
        query = check_input(inputs["query"])
    except InputRejected:
        return {"needs_clarification": True, "blocked": True}
    result = parse_query(query, inputs["mode"])
    return {**result.trip.model_dump(), "needs_clarification": result.needs_clarification}


def same(actual, expected) -> bool:
    if isinstance(expected, str):
        return isinstance(actual, str) and actual.strip().lower() == expected.lower()
    return actual == expected


def field_accuracy(outputs: dict, reference_outputs: dict) -> dict:
    checks = [same(outputs.get(k), v) for k, v in reference_outputs.items()]
    return {"key": "field_accuracy", "score": sum(checks) / len(checks)}


def all_fields_correct(outputs: dict, reference_outputs: dict) -> dict:
    return {"key": "all_fields_correct", "score": int(field_accuracy(outputs, reference_outputs)["score"] == 1)}


def run_local():
    total_fields = correct_fields = perfect = 0
    for case in DATASET:
        outputs = run_parser(case)
        wrong = [f"{k}: got {outputs.get(k)!r}, expected {v!r}"
                 for k, v in case["expected"].items() if not same(outputs.get(k), v)]
        total_fields += len(case["expected"])
        correct_fields += len(case["expected"]) - len(wrong)
        perfect += not wrong
        print(("PASS " if not wrong else "FAIL ") + case["query"])
        for line in wrong:
            print("       " + line)
    print("=" * 60)
    print(f"Field accuracy : {correct_fields}/{total_fields} = {correct_fields / total_fields:.0%}")
    print(f"Perfect queries: {perfect}/{len(DATASET)} = {perfect / len(DATASET):.0%}")


def run_langsmith():
    from langsmith import Client, evaluate

    client = Client()
    if not client.has_dataset(dataset_name=DATASET_NAME):
        client.create_dataset(DATASET_NAME, description="Travel query parser test cases")
        client.create_examples(dataset_name=DATASET_NAME, examples=[
            {"inputs": {"mode": c["mode"], "query": c["query"]}, "outputs": c["expected"]} for c in DATASET
        ])
    evaluate(run_parser, data=DATASET_NAME, evaluators=[field_accuracy, all_fields_correct],
             experiment_prefix="parser")
    print("Done. Open smith.langchain.com -> Datasets -> tripmate-parser to see the experiment.")


if __name__ == "__main__":
    run_langsmith() if "--langsmith" in sys.argv else run_local()
