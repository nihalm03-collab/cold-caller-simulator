from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from raj import get_raj_response


class ConversationMessage(BaseModel):
	role: str = Field(..., min_length=1)
	content: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
	conversation_history: list[ConversationMessage]


class ChatResponse(BaseModel):
	reply: str


class HealthResponse(BaseModel):
	status: str


app = FastAPI()


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
	return HealthResponse(status="ok")


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
	try:
		reply = get_raj_response(
			[message.model_dump() for message in request.conversation_history]
		)
	except ValueError as exc:
		raise HTTPException(status_code=400, detail=str(exc)) from exc
	except RuntimeError as exc:
		raise HTTPException(status_code=502, detail=str(exc)) from exc

	return ChatResponse(reply=reply)