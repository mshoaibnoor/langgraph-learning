
from langchain_core.messages import HumanMessage

inputs = [HumanMessage(content="what is the weather in sf")]
final_message = ""

async for msg, metadata in agent.astream(
    {"messages": [("human", "what items are on the shelf?")]}, stream_mode="messages"
):
    # Stream all messages from the tool node
    if (
        msg.content
        and not isinstance(msg, HumanMessage)
        and metadata["langgraph_node"] == "tools"
        and not msg.name
    ):
        print(msg.content, end="|", flush=True)
    # Final message should come from our agent
    if msg.content and metadata["langgraph_node"] == "agent":
        final_message += msg.content