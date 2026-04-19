# agent-poc-api

Small proof-of-concept CLI app built with the OpenAI Agents SDK.

It runs a local interactive agent that can answer normally, and delegates card limit questions to an external API tool.

## What it does

- Starts a terminal chat loop
- Uses an agent named **Pipeline Orchestrator**
- Calls a custom tool, `limit_agent(message)`, for card limit-related questions
- Sends tool requests to a backend API and keeps a `conversationId` so the remote service can maintain context
- Streams model output back to the terminal as it is generated

## How it works

The app in `main.py`:

1. Loads environment variables with `python-dotenv`
2. Defines a tool function, `limit_agent`
3. Posts tool calls to `LIMIT_API_URL`
4. Creates an agent with that tool attached
5. Runs an interactive REPL until you type `exit` or `quit`

## Requirements

- Python 3.14+
- An environment with the dependencies from `pyproject.toml`
- OpenAI credentials configured for the Agents SDK
- A reachable limit API endpoint

## Dependencies

From `pyproject.toml`:

- `openai-agents`
- `pydantic`
- `python-dotenv`

## Environment variables

Create a `.env` file with the values your environment needs.

### Required

Use whatever OpenAI Agents SDK variables your setup expects, for example:

```env
OPENAI_API_KEY=your_api_key
```

### Optional

```env
LIMIT_API_URL=http://127.0.0.1:8000/api/chat
```

If `LIMIT_API_URL` is not set, the app defaults to `http://127.0.0.1:8000/api/chat`.

## Install

Using `uv`:

```bash
uv sync
```

Or with pip:

```bash
pip install -e .
```

## Run

```bash
python main.py
```

You should then see a prompt like:

```text
You:
```

Type messages interactively. To stop, enter:

```text
exit
```

or

```text
quit
```

## Example flow

- General question → answered directly by the main agent
- Card limit question → routed through `limit_agent`
- The tool sends:
  - `message`
  - `conversationId`
  - `agent: "limit"`

## Project structure

```text
.
├── main.py          # Interactive CLI agent
├── pyproject.toml   # Project metadata and dependencies
├── .env             # Local environment variables
└── README.md
```

## Notes

- Responses are streamed token-by-token in the terminal.
- The remote limit API is expected to return JSON containing `output` and optionally `conversationId`.
- `conversationId` is stored in-memory for the current process only.

## API contract expected by the tool

The tool sends a POST request to:

```text
$LIMIT_API_URL
```

with a JSON body like:

```json
{
  "message": "increase my card limit",
  "conversationId": null,
  "agent": "limit"
}
```

It expects a JSON response shaped like:

```json
{
  "output": "...",
  "conversationId": "..."
}
```

## Limitations

- The app is a local proof of concept, not a production service
- Conversation state is not persisted across restarts
- Error handling is minimal beyond HTTP status checking
