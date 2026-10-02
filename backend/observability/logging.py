import json
import logging
import sys
from contextvars import ContextVar

# Every request gets an ID. It follows the request through all agents and logs.
request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "time": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "message": record.getMessage(),
            "request_id": request_id_var.get(),
        }
        entry.update(getattr(record, "fields", {}))
        return json.dumps(entry, ensure_ascii=False)


def get_logger(name: str = "tripmate") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


def log_event(message: str, **fields):
    get_logger().info(message, extra={"fields": fields})
