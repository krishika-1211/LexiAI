import asyncio
import io
import time

import pyttsx3
import requests
import speech_recognition as sr

TOGETHER_AI_API_KEY = "tgp_v1_F454MgPM8CXXlrEQv4xSxJ66d34q7SqSRofKib2inEI"
GROQ_KEY = "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"

engine = pyttsx3.init()


def speak(response):
    if response:
        print("Assistant:", response)
        engine.say(response)
        engine.runAndWait()


def transcribe_with_groq(audio_data):
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}"}
    files = {"file": ("audio.wav", audio_data, "audio/wav")}
    payload = {"model": "whisper-large-v3", "response_format": "json"}

    response = requests.post(url, headers=headers, files=files, data=payload)
    if response.status_code == 200:
        return response.json().get("text", "")
    else:
        print(f"Groq API Error: {response.status_code}")
        return None


def get_ai_response(query):
    """Generates AI response using Groq API."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "mixtral-8x7b-32768",  # Groq's recommended model for conversational AI
        "messages": [{"role": "user", "content": query}],
        "max_tokens": 10,
        "temperature": 0.7,
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return (
            response.json()
            .get("choices", [{}])[0]
            .get("message", {})
            .get("content", None)
        )
    else:
        print(f"Groq API Error: {response.status_code}")
        return None


async def recognize_and_send(session_id, db, duration: int):
    recognizer = sr.Recognizer()
    end_time = time.time() + duration

    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)

        while time.time() < end_time:
            try:
                audio = await asyncio.to_thread(
                    recognizer.listen, source, timeout=None, phrase_time_limit=3
                )
                audio_data = io.BytesIO(audio.get_wav_data())

                transcription = await asyncio.to_thread(
                    transcribe_with_groq, audio_data
                )
                if not transcription:
                    return {"error": "Could not transcribe audio"}

                print("User:", transcription)

                ai_response = await asyncio.to_thread(get_ai_response, transcription)
                if not ai_response:
                    return {"error": "AI response failed"}

                await asyncio.to_thread(speak, ai_response)

                conversation_entry = {
                    "session_id": session_id,
                    "user_input": transcription,
                    "ai_response": ai_response,
                }
                if db:
                    db.add(conversation_entry)
                    db.commit()

            except sr.UnknownValueError:
                return {"error": "Sorry, I didn't understand that."}

            except sr.WaitTimeoutError:
                return {"error": "Listening timed out."}
