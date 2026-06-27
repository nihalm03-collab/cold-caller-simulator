import os
from typing import Any

from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

RAJ_SYSTEM_PROMPT = (
	"You are Raj Sharma, a 38-year-old Procurement Manager based in Pune, India. "
	"You are on a cold sales call and your default tone is skeptical, busy, and dismissive. "
	"Speak in natural Hinglish (English + Hindi in Roman script), realistic and conversational. "
	"Start short, guarded, and mildly irritated. "
	"Keep every reply concise: 1 to 3 sentences maximum. "
	"Your default objections are: (1) already using Zoho, (2) pricing is too high, "
	"(3) no time right now. "
	"In early turns, challenge vague claims and ask practical questions. "
	"If the caller provides clear ROI, cost savings, or easy low-risk migration details, "
	"gradually become more open over multiple turns. "
	"Do not become friendly too quickly. "
	"If the pitch is convincing and objections are handled well, agree to a short demo as next step. "
	"If unconvinced, politely refuse. "
	"Focus on procurement concerns: savings, implementation effort, migration risk, and timeline."
)


def get_raj_response(conversation_history: list[dict[str, Any]]) -> str:
	"""Generate Raj's response using Google Gemini.

	Args:
		conversation_history: A list of chat messages using OpenAI format,
			e.g. [{"role": "user", "content": "..."}, ...].

	Returns:
		Raj's next reply as a string.

	Raises:
		ValueError: If required Gemini configuration is missing or inputs are invalid.
		RuntimeError: If the model returns an empty response.
	"""
	if not isinstance(conversation_history, list):
		raise ValueError("conversation_history must be a list of message dicts.")

	api_key = os.getenv("GEMINI_API_KEY")
	model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

	if not api_key:
		raise ValueError(
			"Missing required Gemini settings. "
			"Set GEMINI_API_KEY in your .env file."
		)

	for i, msg in enumerate(conversation_history):
		if not isinstance(msg, dict):
			raise ValueError(f"conversation_history[{i}] must be a dict.")
		if "role" not in msg or "content" not in msg:
			raise ValueError(
				f"conversation_history[{i}] must contain 'role' and 'content' keys."
			)

	genai.configure(api_key=api_key)
	model = genai.GenerativeModel(model_name=model_name)

	transcript_lines = ["System instruction:", RAJ_SYSTEM_PROMPT, "", "Conversation so far:"]
	for msg in conversation_history:
		role = str(msg["role"]).strip().lower()
		content = str(msg["content"]).strip()
		if role == "assistant":
			role_label = "Assistant"
		elif role == "user":
			role_label = "User"
		else:
			role_label = role.title() or "User"
		transcript_lines.append(f"{role_label}: {content}")

	transcript_lines.extend(
		[
			"",
			"Now produce Raj's next reply only.",
			"Reply as Raj in 1-3 sentences.",
		]
	)
	prompt = "\n".join(transcript_lines)

	response = model.generate_content(
		prompt,
		generation_config={"temperature": 0.7, "max_output_tokens": 1000},
	)

	content = getattr(response, "text", None)
	if not content:
		raise RuntimeError("Gemini returned an empty response for Raj.")

	return content.strip()
