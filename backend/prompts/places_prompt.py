from langchain_core.prompts import ChatPromptTemplate

places_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an Indian travel expert. List real, well-known tourist places only. "
               "Never invent places. If you know fewer than 8, list fewer."),
    ("human", "List up to 8 famous tourist places in or near {city}, India. Names only."),
])
