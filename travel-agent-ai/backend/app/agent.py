"""
The Travel Agent.

Single agent (by design, for now) using LangChain's tool-calling agent.
This is the file that grows later: swap `build_agent_executor` for a
LangGraph node, add a supervisor that routes to multiple agents like this
one, and the rest of the app (main.py, memory.py, guardrails.py) barely changes.
"""
import os
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from .tools import ALL_TOOLS

SYSTEM_PROMPT = """You are a knowledgeable, friendly AI Travel Planning Agent.

Your job:
- Help users plan trips: destinations, budgets, weather, attractions, day-wise itineraries.
- Use your tools (get_weather, estimate_budget, search_attractions) whenever the user's
  question needs real data rather than a guess.
- Ask a clarifying question if the destination, dates, or budget are missing and you need them.
- Keep answers concrete and structured (use short bullet points or day-by-day lists for itineraries).
- Stay strictly within travel planning topics.
"""


def build_agent_executor() -> AgentExecutor:
    llm = ChatOpenAI(
        model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
        temperature=0.3,
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    agent = create_tool_calling_agent(llm=llm, tools=ALL_TOOLS, prompt=prompt)
    executor = AgentExecutor(agent=agent, tools=ALL_TOOLS, verbose=True, max_iterations=6)
    return executor


# Built once at startup, reused across requests (stateless executor — state lives in DB)
agent_executor = build_agent_executor()
