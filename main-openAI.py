import os
import speech_recognition as sr
from dotenv import load_dotenv
from openai import APIConnectionError, APIStatusError, AuthenticationError, OpenAI


def ask_openai(client: OpenAI, question: str) -> str:
	response = client.responses.create(
		model="gpt-4o-mini",
		input=question,
	)
	return response.output_text.strip()


def listen_and_answer() -> None:
	api_key = os.getenv("OPENAI_API_KEY")
	if not api_key:
		print("Missing OPENAI_API_KEY environment variable.")
		print("Set it first, then run this script again.")
		return

	base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
	if base_url.startswith("http://127.0.0.1") or base_url.startswith("http://localhost"):
		print("OPENAI_BASE_URL points to localhost, which is likely incorrect.")
		print("Remove OPENAI_BASE_URL or set it to https://api.openai.com/v1")
		return

	client = OpenAI(api_key=api_key, base_url=base_url, timeout=30.0, max_retries=1)
	recognizer = sr.Recognizer()

	try:
		microphone = sr.Microphone()
	except OSError:
		print("No microphone found. Please connect a microphone and try again.")
		return

	print("Listening started. Ask your question by speaking.")
	print("Say 'stop' or 'exit' to quit.")
	print("Press Ctrl+C to stop.\n")

	with microphone as source:
		# Reduce noise impact for better recognition.
		recognizer.adjust_for_ambient_noise(source, duration=1)

	while True:
		try:
			with microphone as source:
				audio = recognizer.listen(source)

			text = recognizer.recognize_google(audio)
			print(f"You said: {text}")

			if text.strip().lower() in {"stop", "exit", "quit"}:
				print("Stopping on voice command.")
				break

			try:
				answer = ask_openai(client, text)
				print(f"AI: {answer}\n")
			except APIConnectionError as error:
				print("Could not connect to OpenAI API.")
				print("Check internet, firewall/proxy, and OPENAI_BASE_URL settings.")
				if error.__cause__:
					print(f"Connection details: {error.__cause__}")
			except AuthenticationError:
				print("OpenAI authentication failed. Check OPENAI_API_KEY.")
			except APIStatusError as error:
				print(f"OpenAI API error ({error.status_code}): {error.message}")

		except sr.UnknownValueError:
			print("Could not understand audio.")
		except sr.RequestError as error:
			print(f"Speech service error: {error}")
		except KeyboardInterrupt:
			print("\nStopped listening.")
			break


if __name__ == "__main__":
	load_dotenv()
	listen_and_answer()