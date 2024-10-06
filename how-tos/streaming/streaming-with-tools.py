# https://langchain-ai.github.io/langgraph/how-tos/streaming-events-from-within-tools/

from langchain_core.callbacks import Callbacks
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_ollama import ChatOllama

from langgraph.prebuilt import create_react_agent

@tool
async def get_items(
    place: str, callbacks: Callbacks
) -> str:
    """Use this tool to look up which items are in the given place."""
    template = ChatPromptTemplate.from_messages(
        [
            (
                "human",
                "Can you tell me what kind of items i might find in the following place: '{place}'. "
                "List at least 3 such items separating them by a comma. And include a brief description of each item..",
            )
        ]
    )
    chain = template | llm.with_config(
        {
            "run_name": "Get Items LLM",
            "tags": ["tool_llm"],
            "callbacks": callbacks,  # <-- Propagate callbacks (Python <= 3.10)
        }
    )
    chunks = [chunk async for chunk in chain.astream({"place": place})]
    return "".join(chunk.content for chunk in chunks)

llm = ChatOllama(model='llama3.1:8b')
tools =[get_items]
agent = create_react_agent(llm, tools)

