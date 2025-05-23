import asyncio
from datetime import datetime, timedelta

import pyttsx3
import requests
import speech_recognition as sr
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from src.category.models import Topic
from src.config import Config
from src.conversation.crud import conversation_crud, conversation_session_crud
from src.conversation.models import Report
from src.conversation.utils.score import calculate_score

TOGETHER_AI_API_KEY = Config.TOGETHER_AI_API_KEY
GROQ_KEY = Config.GROQ_KEY


engine = pyttsx3.init()


def speak(response):
    if response:
        print("Assistant:", response)
        print("AI:", response)
        engine.say(response)
        engine.runAndWait()


def transcribe_with_groq(audio_data):
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}"}
    files = {"file": ("audio.wav", audio_data, "audio/wav")}
    payload = {"model": "whisper-large-v3", "response_format": "json"}

    response = requests.post(url, headers=headers, files=files, data=payload)
    if response.status_code == 200:
        data = response.json()
        return data.get("text", ""), data.get("confidence", 0)
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
        "model": "llama3-70b-8192",  # Groq's recommended model for conversational AI
        "messages": [{"role": "user", "content": query}],
        "max_tokens": 20,
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


async def websocket_conversation(
    websocket: WebSocket, db: Session, user, topic_id: str, duration: int
):
    await websocket.accept()

    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        await websocket.send_text("Error: Invalid topic selected.")
        await websocket.close()
        return

    session = conversation_session_crud.create(
        db, user_id=user.id, created_by=user.email, topic_id=topic_id
    )

    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=duration)
    user_messages = []
    stt_confidences = []

    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)

            ai_intro = f"Let's talk about {topic.name}. What do you think about it?"
            speak(ai_intro)
            await websocket.send_text(ai_intro)

            await asyncio.sleep(2)

            while datetime.now() < end_time:
                print("Listening for user input...")
                audio = recognizer.listen(source, timeout=10)
                audio_data = audio.get_wav_data()  # Convert audio to raw bytes

                # Transcribe speech to text
                transcription, confidence = transcribe_with_groq(audio_data) or ("", 0)
                if transcription:
                    user_messages.append(transcription)
                    stt_confidences.append(confidence)
                    print("User:", transcription)

                    conversation_crud.user_conversation(
                        db, session.id, transcription, user.email
                    )

                    # Generate AI response
                    ai_response = get_ai_response(transcription)
                    if ai_response:
                        conversation_crud.ai_conversation(
                            db, session.id, ai_response, user.email
                        )

                        speak(ai_response)

                        # Send AI response back to WebSocket
                        await websocket.send_text(ai_response)
                    else:
                        await websocket.send_text(
                            "Error: AI could not generate a response."
                        )
                else:
                    await websocket.send_text("Error: Could not transcribe audio.")

        await websocket.send_text("Conversation time is up. Disconnecting...")
        await websocket.close()

    except WebSocketDisconnect:
        print(f"User {user.email} disconnected")

    finally:
        total_time = (datetime.now() - start_time).total_seconds() / 60
        session.total_time = round(total_time, 2)

        # Calculate session score and word count
        session_score, total_words = calculate_score(user_messages, stt_confidences)

        # Update Report
        report = db.query(Report).filter(Report.session_id == session.id).first()
        if report:
            report.score = session_score
            report.words_spoken = total_words
        else:
            report = Report(
                user_id=user.id,
                topic_id=topic_id,
                session_id=session.id,
                score=session_score,
                words_spoken=total_words,
                created_by=user.email,
                updated_by=user.email,
            )
            db.add(report)

        db.commit()
        print(f"Session {session.id} - Score: {session_score}, Words: {total_words}")
