import sounddevice as sd
import queue
import sys
import json
from vosk import Model, KaldiRecognizer
import pyttsx3

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Load Vosk model
model = Model("vosk-model-small-en-us-0.15")
rec = KaldiRecognizer(model, 16000)
q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                       channels=1, callback=callback):
    print("Say something...")

    while True:
        data = q.get()
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text = result.get("text", "")
            if text:
                print("You said:", text)

                # Respond
                if "hello" in text:
                    reply = "Hello Adesoji, how can I help you?"
                elif "time" in text:
                    from datetime import datetime
                    now = datetime.now().strftime("%I:%M %p")
                    reply = f"The current time is {now}"
                elif "hi" in text:
                    reply = "How is your day going?"
                elif "weather" in text:
                    reply = "Today's weather is sunny and warm."
                elif "hey"  in text:
                    reply = "Hey back" 
                else:
                    reply = "I did not understand that."

                print("Mirror:", reply)
                engine.say(reply)
                engine.runAndWait()