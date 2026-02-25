import speech_recognition as sr
import pyttsx3

engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio)
        return text

    except sr.UnknownValueError:
        return "Sorry, I couldn't understand that."

    except sr.RequestError:
        return "Speech service unavailable."