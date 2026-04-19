import asyncio
import os

import httpx
from agents import Agent, Runner, function_tool
from dotenv import load_dotenv
from openai.types.responses import ResponseTextDeltaEvent

load_dotenv()

LIMIT_API_URL = os.getenv("LIMIT_API_URL", "http://127.0.0.1:8000/api/chat")
conversation_id: str | None = None


@function_tool
async def limit_agent(message: str) -> str:
    global conversation_id

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            LIMIT_API_URL,
            json={"message": message, "conversationId": conversation_id, "agent": "limit"},
        )
        response.raise_for_status()
        data = response.json()

    conversation_id = data.get("conversationId") or conversation_id
    return data.get("output") or "(no response)"


agent = Agent(
    name="Pipeline Orchestrator",
    instructions="answer with flirt and be playful. Use limit_agent for any card limit question.",
    model="gpt-4o-mini",
    tools=[limit_agent],
)


async def main():
    history = []
    while (msg := input("You: ")).strip().lower() not in {"exit", "quit"}:
        history.append({"role": "user", "content": msg})
        result = Runner.run_streamed(agent, history)
        print("Agent: ", end="", flush=True)
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                print(event.data.delta, end="", flush=True)
        print()
        history = result.to_input_list()


if __name__ == "__main__":
    asyncio.run(main())
