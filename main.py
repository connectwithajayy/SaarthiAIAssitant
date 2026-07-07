import os
import speech_recognition as sr
from dotenv import load_dotenv
import google.generativeai as genai


def speak_text(text: str) -> None:
	"""Speak text directly using pyttsx3 without creating an MP3 file."""
	try:
		import pyttsx3
	except ImportError as exc:
		raise RuntimeError("pyttsx3 is not installed. Install it with: pip install pyttsx3") from exc

	engine = pyttsx3.init()
	engine.say(text)
	engine.runAndWait()


def ask_gemini(model: genai.GenerativeModel, question: str) -> str:
	response = model.generate_content(question)
	if hasattr(response, "text") and response.text:
		return response.text.strip()
	return "I could not generate a response."


def listen_and_answer() -> None:
	api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
	if not api_key:
		print("Missing GEMINI_API_KEY environment variable.")
		print("Set it first, then run this script again.")
		return

	genai.configure(api_key=api_key)
	model = genai.GenerativeModel("gemini-3.5-flash")
	recognizer = sr.Recognizer()
	
    

	try:
		microphone = sr.Microphone()
	except OSError:
		print("No microphone found. Please connect a microphone and try again.")
		return


    
	print("Saarthi Ai Assistant")
	print("--------------------------------------------------------------")
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
				answer = ask_gemini(model, text)
				print(f"AI: {answer}\n")
				speak_text(answer)
			except Exception as error:
				print(f"Gemini API error: {error}")

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