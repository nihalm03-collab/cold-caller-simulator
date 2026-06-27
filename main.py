from raj import get_raj_response
from voice import listen_speech, speak_text

_EXIT_PHRASES = {"quit", "bye", "goodbye"}


def main() -> None:
	conversation_history: list[dict[str, str]] = []

	print("Cold Caller Simulator started. Say 'quit' or 'bye' to exit.")

	while True:
		print("Listening...")
		try:
			user_text = listen_speech().strip()
		except Exception as exc:
			print(f"[Listen error]: {exc}")
			continue

		if not user_text:
			continue

		print(f"You: {user_text}")

		if user_text.lower().strip(".,!? ") in _EXIT_PHRASES:
			print("Exiting simulator.")
			break

		conversation_history.append({"role": "user", "content": user_text})

		try:
			raj_reply = get_raj_response(conversation_history)
		except Exception as exc:
			print(f"[Raj error]: {exc}")
			continue

		print(f"Raj: {raj_reply}")
		speak_text(raj_reply)
		conversation_history.append({"role": "assistant", "content": raj_reply})


if __name__ == "__main__":
	main()
