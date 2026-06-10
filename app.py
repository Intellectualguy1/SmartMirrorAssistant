import streamlit as st
import cv2
import numpy as np
from deepface import DeepFace
from vosk import Model, KaldiRecognizer
import sounddevice as sd
import queue
import pyttsx3
import json
from datetime import datetime
import time

# Streamlit UI setup
st.set_page_config(page_title="Smart Mirror", layout="centered")
st.title("Smart Mirror Assistant")

video_placeholder = st.empty()
status_placeholder = st.empty()
voice_placeholder = st.empty()

# TTS
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)

# Vosk setup
vosk_model = Model("vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(vosk_model, 16000)
audio_queue = queue.Queue()

def mic_callback(indata, frames, time, status):
    audio_queue.put(bytes(indata))

# Webcam
cap = cv2.VideoCapture(0)
recognized = False

# Start Mirror
if st.button("Start Smart Mirror"):
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # FACE RECOGNITION
        if not recognized:
            try:
                result = DeepFace.find(frame, db_path="faces", enforce_detection=False)
                if len(result) > 0:
                    status_placeholder.success("✅ Face recognized: Hello Adesoji!")
                    recognized = True
            except:
                pass

        # Show camera feed
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = cv2.resize(frame_rgb, (640, 480))
        video_placeholder.image(frame_rgb, channels="RGB")

        # Once recognized, enter voice loop
        if recognized:
            with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                                   channels=1, callback=mic_callback):
                voice_placeholder.info("🎤 Listening... Speak now.")

                start_time = time.time()
                captured_audio = b""

                while time.time() - start_time < 5:
                    data = audio_queue.get()
                    captured_audio += data
                    if recognizer.AcceptWaveform(data):
                        break

                if recognizer.AcceptWaveform(captured_audio):
                    result = json.loads(recognizer.Result())
                    spoken_text = result.get("text", "")

                    if spoken_text:
                        voice_placeholder.markdown(f"**You said:** {spoken_text}")

                        # Smart Mirror response logic
                        if "hello" in spoken_text:
                            reply = "Hello Adesoji, how can I help you?"
                        elif "time" in spoken_text:
                            now = datetime.now().strftime("%I:%M %p")
                            reply = f"The current time is {now}"
                        elif "weather" in spoken_text:
                            reply = "Today’s weather is sunny and warm."
                        elif "stop" in spoken_text or "exit" in spoken_text:
                            reply = "Goodbye!"
                            voice_placeholder.markdown(f"**Mirror:** {reply}")
                            tts_engine.say(reply)
                            tts_engine.runAndWait()
                            break  # Stop loop
                        else:
                            reply = "Sorry, I didn’t understand that."

                        voice_placeholder.markdown(f"**Mirror:** {reply}")
                        tts_engine.say(reply)
                        tts_engine.runAndWait()
                    else:
                        voice_placeholder.warning("⚠️ No voice recognized.")
                else:
                    voice_placeholder.warning("⚠️ Could not understand speech.")

    cap.release()

