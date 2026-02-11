from langchain.agents import create_agent
from tools import retrieve_text_context, retrieve_by_inventory, search_image_by_text, search_by_image_and_explain
from llm_model import llm

tools = [
    retrieve_text_context,
    retrieve_by_inventory,
    search_image_by_text,
    # hybrid_search,
    search_by_image_and_explain  
]

system_prompt = """
You are an AI assistant for the Royal Commission for AlUla.
You help users explore the AlUla Collections - 100 Objects.

You can:
- Retrieve object metadata
- Search by inventory number
- Search visually similar artifacts
- Combine metadata and image results

Always use tools when needed.
"""

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt
)
