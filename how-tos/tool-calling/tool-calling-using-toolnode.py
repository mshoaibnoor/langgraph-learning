from langchain_core.messages import AIMessage
from langchain_core.tools import tool

from langgraph.prebuilt import ToolNode

@tool
def get_weather(location: str):
    """Call to get the current weather."""
    if location.lower() in ["sf", "san francisco"]:
        return "It's 60 degrees and foggy."
    else:
        return "It's 90 degrees and sunny."
    
@tool
def get_coolest_cities():
    """Get a list of coolest cities"""
    return "nyc, sf"

tools = [get_weather, get_coolest_cities]
tool_node = ToolNode(tools)

# with single tool call
# message_with_single_tool_call = AIMessage(
#     content='',
#     tool_calls = [
#         {
#          "name": "get_weather",
#          "args": {"location": "sf"},
#          "id": "tool_call_id",
#          "type": "tool_call",
#     }],
# )

# result = tool_node.invoke({"messages": [message_with_single_tool_call]})
# print(result)

# with multiple tool call
# message_with_multiple_tool_calls = AIMessage(
#     content="",
#     tool_calls = [
#         {
#             "name": "get_coolest_cities",
#             "args": {},
#             "id": "tool_call_id_1",
#             "type": "tool_call",
#         },
#         {
#             "name": "get_weather",
#             "args": {"location": "sf"},
#             "id": "tool_call_id_2",
#             "type": "tool_call",
#         },
#     ],
# )
# result_multiple = tool_node.invoke({"messages": [message_with_multiple_tool_calls]})

# print(result_multiple)


#-----------------------#
# using with chat models
from typing import Literal

from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, MessageGraph
from langgraph.prebuilt import ToolNode

model_with_tools = ChatOllama(model='llama3.1:8b', temperature=0).bind_tools(tools)

# result_weather = model_with_tools.invoke("what's the weather in sf?").tool_calls
# print(result_weather)

# tn = tool_node.invoke({"messages":[model_with_tools.invoke("what's the weather in sf?")]})
# print(tn)

# result_city = model_with_tools.invoke("what is the coolist city?").tool_calls
# print(result_city)


#---------------#
# ReAct Agent

from typing import Literal

from langgraph.graph import StateGraph, MessagesState, START, END

def should_continue(state: MessagesState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

def call_model(state: MessagesState):
    messages = state["messages"]
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}

workflow = StateGraph(MessagesState)

# Define the two nodes we will cycle between
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, ["tools", END])
workflow.add_edge("tools", "agent")

app = workflow.compile()

# example with a single tool call
# for chunk in app.stream(
#     {"messages": [("human", "what's the weather in sf?")]}, stream_mode="values"
# ):
#     chunk["messages"][-1].pretty_print()


# example with a multiple tool calls in succession

for chunk in app.stream(
    {"messages": [("human", "what's the weather in the coolest cities?")]},
    stream_mode="values",
):
    chunk["messages"][-1].pretty_print()