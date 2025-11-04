import json
from typing import List, Annotated, Dict
from typing_extensions import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from . import rag_service

load_dotenv()

# CHANGED: We now have only ONE, very strict system prompt.
SYSTEM_PROMPT = """You are a professional assistant who answers questions strictly based on the provided document context.
Your goal is to be accurate and faithful to the source material.
If the answer is not in the provided context, you MUST state: 'The provided documents do not contain information on that topic.'
Do not use any of your outside general knowledge to answer questions."""


# --- (Agent State, LLM, Nodes, and Graph Creation are mostly the same) ---
class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], lambda x, y: x + y]

def get_llm(llm_model_name: str = "gpt-4o"):
    return ChatOpenAI(model=llm_model_name, streaming=True)

def generate_node(state: AgentState, config):
    llm = get_llm(config["configurable"].get("llm_model_name"))
    return {"messages": [llm.invoke(state["messages"])]}

def retrieve_node(state: AgentState):
    last_message = state["messages"][-1].content
    retriever = rag_service.get_retriever()
    retrieved_docs = retriever.invoke(last_message)
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])
    # Prepend the instruction to the context for the LLM
    context_message = SystemMessage(content=f"Context from documents:\n\n{context}")
    return {"messages": [context_message]}

def create_rag_chatbot_graph():
    graph_builder = StateGraph(AgentState)
    graph_builder.add_node("retrieve", retrieve_node)
    graph_builder.add_node("generate", generate_node)
    graph_builder.set_entry_point("retrieve")
    graph_builder.add_edge("retrieve", "generate")
    graph_builder.add_edge("generate", END)
    return graph_builder.compile()

# We only need the RAG agent now.
available_agents: Dict[str, any] = {
    "chatbot_rag_lite": create_rag_chatbot_graph(),
}
# --- (End of major changes) ---


# --- Agent Execution Functions (Simplified) ---
# The 'character' and 'agent_name' arguments are no longer needed as they are now fixed.

async def run_agent_text_stream(message: str, history: List[dict], llm_model_name: str):
    agent = available_agents["chatbot_rag_lite"]
    messages_for_agent = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=message)]
    inputs = {"messages": messages_for_agent}
    config = {"configurable": {"llm_model_name": llm_model_name}}
    
    full_response = ""
    async for event in agent.astream_events(inputs, config=config, version="v1"):
        if event["event"] == "on_chat_model_stream":
            chunk = event["data"]["chunk"]
            if chunk.content:
                full_response += chunk.content
                yield f"data: {json.dumps({'type': 'token', 'delta': chunk.content})}\n\n"
    history.append({"role": "assistant", "content": full_response})
    yield f"data: {json.dumps({'type': 'done'})}\n\n"

async def run_agent_sync(message: str, history: List[dict], llm_model_name: str) -> str:
    agent = available_agents["chatbot_rag_lite"]
    messages_for_agent = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=message)]
    inputs = {"messages": messages_for_agent}
    config = {"configurable": {"llm_model_name": llm_model_name}}
    
    result = await agent.ainvoke(inputs, config=config)
    final_response = result['messages'][-1].content
    history.append({"role": "assistant", "content": final_response})
    return final_response