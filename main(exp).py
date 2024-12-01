import joblib
import pyttsx3
import datetime
import wikipedia
import webbrowser
import os
import struct
import subprocess
import pvporcupine
import pyaudio
import speech_recognition as sr
import pyautogui
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import tkinter as tk
from tkinter import scrolledtext
import time
import requests
import pyperclip
import time
import keyboard
import pymongo
# Data for the model
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['ai_asistant']  # Create or access the database
collection = db['com']
def fetch_commands_from_db():
    """Fetch commands and intents from MongoDB."""
    commands_data = list(collection.find({}))
    commands = [item['command'] for item in commands_data]
    intents = [item['intent'] for item in commands_data]
    return commands, intents

# Fetch commands and intents from the database
commands, intents = fetch_commands_from_db()

# Train the model
X_train, X_test, y_train, y_test = train_test_split(commands, intents, test_size=0.2, random_state=42)
model = make_pipeline(TfidfVectorizer(), MultinomialNB())
model.fit(X_train, y_train)
joblib.dump(model, 'intent_model.pkl')

# Initialize recognizer and TTS engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()
engine.setProperty('rate', 210)
engine.setProperty('volume', 1)
chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"

# Load the trained model
model = joblib.load('intent_model.pkl')
def get_weather(city):
    api_key = "30fb90a564464659a2d134443242508"  # Replace with your actual API key
    base_url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"
    
    try:
        response = requests.get(base_url)
        response.raise_for_status()  # Check for HTTP errors
        weather_data = response.json()
        
        if 'error' in weather_data:
            print(f"Error: {weather_data['error']['message']}")
            return

        temp_c = weather_data['current']['temp_c']
        condition = weather_data['current']['condition']['text']
        print(f"The temperature in {city} is {temp_c}°C with {condition}.")
        
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch weather data: {e}")



def classify_intent(command):
    return model.predict([command])[0]

def initialize_porcupine(access_key, keyword_paths):
    return pvporcupine.create(access_key=access_key, keyword_paths=keyword_paths)

def get_audio_stream(porcupine):
    pa = pyaudio.PyAudio()
    try:
        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )
        return pa, audio_stream
    except Exception as e:
        print(f"Failed to open audio stream: {e}")
        speak("Failed to open audio stream.")
        pa.terminate()
        raise
def listen_for_wake_word(porcupine, audio_stream):
    pcm = audio_stream.read(porcupine.frame_length)
    pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
    return porcupine.process(pcm)
def list_voices():
    """List available voices"""
    voices = engine.getProperty('voices')
def set_voice(voice_index=0):
    """Set the desired voice based on index"""
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[voice_index].id)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def greet_user():
    hour = datetime.datetime.now().hour
    if hour < 12:
        speak("Good morning! I am Treshara. How can I assist you today?")
    elif hour < 18:
        speak("Good afternoon!")
    else:
        speak("Good evening!")

def take_command():
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=15, phrase_time_limit=10)
            try:
                command = recognizer.recognize_google(audio)
                print(f"User said: {command}\n")
                return command.lower()
            except sr.UnknownValueError:
                print("Sorry, I did not understand that.")
                speak("Sorry, I did not understand that.")
                return None
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
                speak("Sorry, my speech service is down.")
                return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        speak("An unexpected error occurred.")
        return None
def execute_command(intent):
    if intent == 'open_YouTube':
        webbrowser.open("https://www.youtube.com")
        speak("Opening YouTube")
    elif intent == 'get_time':
        strTime = datetime.datetime.now().strftime("%H:%M:%S")
        speak(f"The time is {strTime}")
    elif intent == 'open_google':
        webbrowser.get(chrome_path).open("https://www.google.com")
        speak("Opening Google")
    elif intent == 'open_file_manager':
        os.startfile(os.getenv('WINDIR') + '\\explorer.exe')
        speak("Opening File Manager")
    elif intent == 'open_visual_studio':
        codePath = r"C:\Users\Asus\python\eswar all\p3.py"
        os.startfile(codePath)
        speak("Opening Visual Studio Code")
    
def execute_command2(intent):
    if intent == 'open_word':
        speak("Opening Word")
        Path = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Word.lnk"
        os.startfile(Path)
    elif intent == 'open_microsoft_store':
        speak("Opening Microsoft Store")
        os.system("start ms-windows-store:")
    elif intent == 'open_excel':
        speak("Opening Excel")
        Path = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Excel.lnk"
        os.startfile(Path)
    elif intent == 'open_powerpoint':
        speak("Opening PowerPoint")
        Path = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\PowerPoint.lnk"
        os.startfile(Path)
    elif intent == 'open_one_note':
        speak("Opening OneNote")
        Path = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\OneNote.lnk"
        os.startfile(Path)
def execute_command3(intent):
    if intent == 'open_network_settings':
        speak("Opening Network Settings")
        os.system("start ms-settings:network")
    elif intent == 'open_settings':
        os.system("start ms-settings:")
        speak("Opening Settings")
    elif intent == 'open_bluetooth_settings':
        speak("Opening Bluetooth Settings")
        os.system("start ms-settings:bluetooth")
    elif intent == 'open_privacy_settings':
        speak("Opening Privacy Settings")
        os.system("start ms-settings:privacy")
def execute_keyboard_command(intent):
    """Execute keyboard operations based on user input."""
    if intent=='type':
        text_to_type = intent.replace('type', '').strip()
        pyautogui.typewrite(text_to_type)
        speak(f"Typing: {text_to_type}")
    elif intent=='press_enter':
        pyautogui.press('enter')
        speak("Pressing Enter")
    elif intent=='press_tab':
        pyautogui.press('tab')
        speak("Pressing Tab")
    elif intent=='press_escape':
        pyautogui.press('esc')
        speak("Pressing Escape")
    elif intent== 'wikipedia':
        execute_wikipedia_command(intent)
def execute_command4(intent,command):
    if intent== 'press':
        key_to_press = intent.replace('press', '').strip()
        pyautogui.press(key_to_press)
        speak(f"Pressing {key_to_press}")
    elif intent == 'close_google':
        speak("Closing Google Chrome")
        subprocess.call(["taskkill", "/F", "/IM", "chrome.exe"])
    elif intent =='search':
        search_query = command.replace("search", "").strip()
        search_url = f"https://www.google.com/search?q={search_query}"
        webbrowser.get(chrome_path).open(search_url)
        speak(f"Searching for {search_query} on Google")
        speak(f"Searching for {search_query} on Google")
    elif intent == 'open_chatgpt':
        webbrowser.open("https://www.chatgpt.com")
        speak("Opening Chat GPT")
    elif intent == 'weather':
        city = input(speak(f"type city name:"))  # Replace with dynamic input or a default city
        get_weather(city)
    elif intent=='enter':
        file_path = r"C:/Users/Asus/Desktop/python.txt"
        def monitor_clipboard():
            previous_clipboard = pyperclip.paste()  # Get initial clipboard content

            while True:
                current_clipboard = pyperclip.paste()
        
                if current_clipboard != previous_clipboard:  # Check if the clipboard content has changed
                    print("New content copied:", current_clipboard)
                    save_to_file(current_clipboard)  # Save copied content to the file
                    previous_clipboard = current_clipboard  # Update the previous clipboard content
        
                time.sleep(1)  # Pause briefly before checking again

        def save_to_file(text):
            with open(file_path, "a") as file:  # Open the file in append mode
                file.write(text + "\n")  # Write the clipboard content to the file
                speak(f"Content saved to {file_path}")

# Monitor for 'Ctrl+C' or 'Command+C'
        def on_copy_press():
            monitor_clipboard()  # Start monitoring clipboard when 'Ctrl+C' is pressed

        keyboard.add_hotkey('ctrl+c', on_copy_press)

# Keep the script running
        keyboard.wait('esc')  # Stop the program if 'Esc' key is pressed
def execute_wikipedia_command(command):
    if 'wikipedia' in command:
        speak('Searching Wikipedia...')
        search_query = command.replace("wikipedia", "").strip()
        if not search_query:
            speak("Please provide a term to search on Wikipedia.")
            return
        try:
            results = wikipedia.summary(search_query, sentences=2)
            speak("According to Wikipedia")
            speak(results)
        except wikipedia.exceptions.DisambiguationError as e:
            speak("The search term is ambiguous. Please be more specific.")
        except wikipedia.exceptions.PageError:
            speak("The page does not exist on Wikipedia.")
        except Exception as e:
            speak("An unknown error occurred.")
            print(f"An error occurred: {e}") 
class VoiceAssistantApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Voice Assistant")
        self.geometry("400x300")
        self.create_widgets()
        self.running = False

    def create_widgets(self):
        self.text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=40, height=10)
        self.text_area.pack(pady=10)
        self.start_button = tk.Button(self, text="Start Listening", command=self.start_listening)
        self.start_button.pack(pady=10)
        self.stop_button = tk.Button(self, text="Stop Listening", command=self.stop_listening)
        self.stop_button.pack(pady=10)

    def start_listening(self):
        self.running = True
        self.text_area.insert(tk.END, "Listening for wake word...\n")
        self.update()
        self.listen_for_commands()

    def stop_listening(self):
        self.running = False

    def listen_for_commands(self):
      ACCESS_KEY = 'vPF9bQqxYb7tBEaRk3Sok1UqO8ljrQAB3j/8f1/oaJM07zf4UWIHoA=='
      keyword_paths = [r"C:\Users\Asus\Downloads\amigo_en_windows_v3_0_0\amigo_en_windows_v3_0_0.ppn"]
      porcupine = initialize_porcupine(ACCESS_KEY, keyword_paths)
      pa, audio_stream = get_audio_stream(porcupine)
      greet_user()

      try:
          while self.running:
              try:
                  if listen_for_wake_word(porcupine, audio_stream) >= 0:
                    speak("Yes, how can I help you?")
                    while True:
                        command = take_command()
                        if command is None:  # Check if the command is None
                            break
                        if command == 'exit':
                            speak("Goodbye!")
                            self.stop_listening()
                            break
                        intent = classify_intent(command)
                        execute_command(intent)
                        execute_command2(intent)
                        execute_command3(intent)
                        execute_command4(intent,command)
                        execute_keyboard_command(intent)
                        
                        if 'wikipedia' in command:
                            execute_wikipedia_command(command)
                        time.sleep(1)  # Brief pause to ensure commands don't overlap

                    self.text_area.insert(tk.END, "Listening for wake word...\n")
                    self.update()
              except OSError as e:
                print(f"Audio stream error: {e}")
                speak("Audio stream error occurred.")
                break
      finally:
        audio_stream.close()
        pa.terminate()
        porcupine.delete()

if __name__ == "__main__":
    list_voices()
    set_voice(1) 
    app = VoiceAssistantApp()
    app.mainloop()

