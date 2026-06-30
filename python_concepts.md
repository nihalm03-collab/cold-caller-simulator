# Python Concepts Cheat Sheet

This project is a good place to learn beginner Python because it uses real code for APIs, voice input, environment variables, and structured data. The examples below are either taken directly from this project or are very small variations of the same ideas.

## Type Hints

Type hints describe what kind of data a function expects and returns. They do not force Python to behave differently at runtime, but they make code easier to read and help tools catch mistakes.

Example from this project:

```python
def get_raj_response(conversation_history: list[dict[str, Any]]) -> str:
    ...
```

What it means:

- `conversation_history` should be a list
- each item in that list should be a dictionary
- the dictionary keys should be strings
- the function returns a string

Another simple example:

```python
def health() -> HealthResponse:
    return HealthResponse(status="ok")
```

This tells readers that `health()` returns a `HealthResponse` object.

## List Comprehensions

A list comprehension is a short way to build a new list from an existing one.

Example from `app.py`:

```python
[message.model_dump() for message in request.conversation_history]
```

This means:

- loop through each `message` in `request.conversation_history`
- call `model_dump()` on each one
- collect the results into a new list

The longer version would be:

```python
messages = []
for message in request.conversation_history:
    messages.append(message.model_dump())
```

## try/except

`try/except` lets your program recover from errors instead of crashing immediately.

Example from `app.py`:

```python
try:
    reply = get_raj_response(
        [message.model_dump() for message in request.conversation_history]
    )
except ValueError as exc:
    raise HTTPException(status_code=400, detail=str(exc)) from exc
except RuntimeError as exc:
    raise HTTPException(status_code=502, detail=str(exc)) from exc
```

What is happening:

- the code tries to generate Raj's reply
- if the input is bad, it catches `ValueError`
- if the model fails, it catches `RuntimeError`
- FastAPI returns a clean API error instead of a raw crash

Another example from `main.py` uses the same idea for microphone or model errors.

## f-strings

An f-string lets you put variables directly inside a string.

Example from `raj.py`:

```python
transcript_lines.append(f"{role_label}: {content}")
```

If `role_label` is `User` and `content` is `Hello`, the result becomes:

```python
"User: Hello"
```

Another example from `voice.py`:

```python
"Authorization": f"Bearer {api_key}"
```

This builds an HTTP header using the real API key.

## Dictionaries

A dictionary stores data as key-value pairs.

Example from this project:

```python
{"role": "user", "content": user_text}
```

This is used to store one message in the conversation history.

Another example from `voice.py`:

```python
headers = {
    "Authorization": f"Bearer {api_key}",
    "Cartesia-Version": "2024-06-10",
}
```

Why dictionaries are useful here:

- they group related values together
- keys like `role`, `content`, and `Authorization` make the data self-explanatory
- they work well for JSON APIs

## *args Unpacking

`*args` is used when a function should accept any number of positional arguments. Python also uses `*` to unpack a list into separate values.

This project does not currently use `*args` directly, but here is a small example using the same conversation idea:

```python
def print_messages(*messages: str) -> None:
    for message in messages:
        print(message)

latest_lines = [
    "You: Hello",
    "Raj: Haan bolo, jaldi bolo.",
]

print_messages(*latest_lines)
```

What happens:

- `latest_lines` is a list
- `*latest_lines` unpacks that list
- the function receives each item as a separate argument

Without unpacking, Python would treat the whole list as one argument.

## async/await

`async` and `await` are used for asynchronous code. This is helpful when a program spends time waiting for network calls, files, or other slow operations.

This project's current endpoints use normal `def`, but FastAPI also supports `async def`.

Example adapted from `app.py`:

```python
@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
```

Simple idea:

- `async def` creates an asynchronous function
- `await` is used inside it when waiting for another async operation
- this can help a web app handle many requests more efficiently

Example with `await`:

```python
async def fetch_reply() -> str:
    reply = await some_async_function()
    return reply
```

Your project does not need this yet, but it is a common next step for API apps.

## Pydantic Models

Pydantic models define the shape of data for requests and responses. FastAPI uses them to validate JSON automatically.

Example from `app.py`:

```python
class ConversationMessage(BaseModel):
    role: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
```

What this does:

- creates a structured model for one chat message
- requires `role` and `content`
- makes sure both values are strings
- rejects empty strings

Another example:

```python
class ChatRequest(BaseModel):
    conversation_history: list[ConversationMessage]
```

This means the `/chat` endpoint expects JSON like this:

```json
{
  "conversation_history": [
    {"role": "user", "content": "Hello Raj"}
  ]
}
```

## Environment Variables with os.getenv

Environment variables let you keep secrets and settings outside your code. This project uses them for API keys, model names, and provider settings.

Example from `raj.py`:

```python
api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
```

What this means:

- `os.getenv("GEMINI_API_KEY")` reads the API key from the environment
- if the key does not exist, it returns `None`
- `os.getenv("GEMINI_MODEL", "gemini-2.5-flash")` uses a default value if nothing is set

Another example from `voice.py`:

```python
sample_rate = int(os.getenv("MIC_SAMPLE_RATE", "16000"))
```

This lets you change microphone settings without editing Python code.

## Quick Summary

- Type hints explain expected data types.
- List comprehensions build lists in a compact way.
- `try/except` handles errors safely.
- f-strings build readable strings with variables.
- Dictionaries store related data using keys and values.
- `*args` and `*` unpacking help pass variable numbers of values.
- `async/await` supports non-blocking work in API apps.
- Pydantic models validate JSON data automatically.
- `os.getenv` reads settings from the environment.