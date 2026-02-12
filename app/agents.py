from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.structured_output import ToolStrategy

from tools import retrieve_text_context, retrieve_by_inventory, search_image_by_text, search_by_image_and_explain
from llm_model import llm
from response_schemas import AlulaResponse

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

After using tools, always return a structured response:

- answer: final explanation
- image_paths: list of image file paths from metadata
- inv_no: matched inventory number if available
- confidence: optional similarity confidence if available
"""

# Set up memory
checkpointer = InMemorySaver()

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt,
    response_format=ToolStrategy(AlulaResponse),
    # checkpointer=checkpointer
)

image_search_system_prompt = """
You are an AI assistant for the Royal Commission for AlUla.
You help users explore the AlUla Collections - 100 Objects.

You can:
- Retrieve object metadata
- Search by inventory number
- Search visually similar artifacts
- Combine metadata and image results

Always use tools when needed.
"""


image_search_tools = [
    search_by_image_and_explain  
]

image_search_agent = create_agent(
    model=llm,
    tools=image_search_tools,
    system_prompt=image_search_system_prompt,
    # response_format=ToolStrategy(AlulaResponse),
)