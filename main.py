# run_pipeline.py
import asyncio
import httpx
from agents import Agent, Runner, function_tool
from dotenv import load_dotenv
load_dotenv()


LIMIT_API_URL = "http://127.0.0.1:8000/api/chat"
_limit_conversation_id: str | None = None


@function_tool
async def limit_agent(message: str) -> str:
    """
    Handles viewing, changing, or managing card limits (POS, ATM, E-commerce). Use when the user wants to see their current limits or make changes.
    """
    global _limit_conversation_id
    payload = {"message": message, "conversationId": _limit_conversation_id, "agent": "limit"}
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(LIMIT_API_URL, json=payload)
        r.raise_for_status()
        data = r.json()
    _limit_conversation_id = data.get("conversationId") or _limit_conversation_id
    return data.get("output") or "(no response)"


orchestrator = Agent(
    name="Pipeline Orchestrator",
    instructions="answer with flirt and be playful. Use the limit_agent tool for any card and limit questions.",
    model="gpt-4o-mini",
    tools=[limit_agent],
)


# ── Run ─────────────────────────────────────────

async def main():
    history = []
    while (msg := input("You: ")).strip().lower() not in {"exit", "quit"}:
        history.append({"role": "user", "content": msg})
        result = await Runner.run(orchestrator, history)
        print(f"Agent: {result.final_output}")
        history = result.to_input_list()


if __name__ == "__main__":
    asyncio.run(main())