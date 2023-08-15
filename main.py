### CONFIG ###
AUTO_PIP = True
##############

import pkg_resources
import importlib

def auto_pip():
    installed_packages = {package.project_name: package.version for package in pkg_resources.working_set}

    with open('requirements.txt') as f:
        required_libraries = [line.strip() for line in f.readlines()]

    for library in required_libraries:
        if library not in installed_packages:
            print(f"\033[31m{library} is not found from pip list try import {library}.\033[0m")
            try:
                importlib.import_module(library)
            except ImportError:
                print(f"\033[31m{library} is not installed. install {library}.\033[0m")
                import pip._internal
                pip._internal.main(['install', library])
                print(f"\033[31m{library} was installed successfully!\033[0m")
            else:
                print(f"\033[31m{library} is already installed!\033[0m")

if AUTO_PIP: auto_pip()

from dotenv import load_dotenv
import speech_recognition as sr
from gtts import gTTS
import os
from langchain.llms import OpenAI
from langchain.agents import initialize_agent
from langchain.chains.conversation.memory import ConversationBufferMemory
from colorama import init
from colorama import Fore, Back
import vosk
import pyaudio
import json
from os import environ
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1" 
import pygame

# Manual set API key, if you don't want to use .env file
# os.environ["OPENAI_API_KEY"] = ""

class Audio:
    def __init__(self, language="en", stt_publish=False, min=10, max_try=3):
        error_count = 0
        print("Audio module loading...\r", end="")
        try:
            init(autoreset=True)
            self.recognizer = sr.Recognizer()
            self.language = language
            self.stt_publish = stt_publish
            self.min = min
            self.max_try = max_try
            vosk.SetLogLevel(-1)
            self.model = vosk.Model(lang=self.language)
            pygame.mixer.init()
            load_dotenv()
            print(Fore.GREEN + "Audio module loaded!   ")
        except Exception as e:
            error_count += 1
            print(f"\033[31mInitialize Error Occurred! {str(e)}\n\n Restart initializing...\033[0m")
            if error_count > self.max_try:
                raise Exception("Too many errors")
            self.__init__()

    def vosk(self):
        error_count = 0
        print(Fore.GREEN + "VOSK Loading...")
        print(Fore.GREEN + "Opening Microphone...\r", end="")
        try:
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=8000,
            )
            recognizer = vosk.KaldiRecognizer(self.model, 16000)
            print(Fore.GREEN + "VOSK Loaded! Start Listening...")
        except:
            error_count += 1
            print(Fore.RED + "Failed to open Microphone!")
            if error_count > self.max_try:
                raise Exception("Too many errors")
            self.vosk()

        text = ""

        while True:
            data = stream.read(8000)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                result_dict = json.loads(result)["text"]
                text += result_dict
                print(result)
                if len(result_dict) > self.min and not self.stt_publish:
                    break
            else:
                result = recognizer.PartialResult()
                result_dict = json.loads(result)["partial"]
                print(result)
            final = json.loads(recognizer.FinalResult())["text"]
            
            if self.stt_publish:
                # publish to server
                pass
        return final

    def stt(self):
        error_count = 0
        print(Fore.CYAN + "Google SpeechRecognition API Preparing...")
        with sr.Microphone() as source:
            print(Fore.GREEN + "Listening...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)

        try:
            recognized_text = self.recognizer.recognize_google(audio, language=self.language)
            print(Fore.CYAN + f"Recognized: {recognized_text}")
            return recognized_text
        except sr.UnknownValueError:
            print(Fore.RED + "Google Speech Recognition could not understand the audio.")
            error_count += 1
            if error_count > self.max_try:
                raise Exception("Too many errors")
            self.stt()
        except sr.RequestError as e:
            print(Fore.RED + f"Could not request results from Google Speech Recognition service; {e}")
            error_count += 1
            if error_count > self.max_try:
                raise Exception("Too many errors")
            self.stt()
        except Exception as e:
            print(Fore.RED + f"An unknown error occurred: {e}")
            self.vosk()

    def tts(self, text):
        error_count = 0
        print(Fore.CYAN + "TTS Loading...                     \r", end="")
        audio_path = "output.mp3"
        try:
            tts = gTTS(text=text, lang=self.language)
            tts.save(audio_path)
            print(Fore.CYAN + "TTS Loaded!\r", end="")
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                print(Fore.GREEN + "Start Playing...\r", end="")
                continue
        except Exception as e:
            error_count += 1
            print(Fore.RED + f"An unknown error occurred: {e}")
            if error_count > self.max_try:
                raise Exception("Too many errors")
            self.tts(text)
        print(Fore.GREEN + "TTS Played! removing audio file...\r", end="")
        os.remove(audio_path)
    
    def llm(self, text, prompt):
        error_count = 0
        print(Fore.WHITE + "LLM Loading...\r", end="")
        try:
            self.llm = OpenAI()
            self.agent = initialize_agent(
                tools=[],
                llm=self.llm, 
                agent="conversational-react-description", 
                memory=ConversationBufferMemory(memory_key="chat_history"),
                agent_kwargs={
                    "prefix": prompt
                }
            )
        except Exception as e:
            error_count += 1
            print(Fore.RED + f"An unknown error occurred: {e}")
            if error_count > self.max_try:
                raise Exception("Too many errors")
            self.llm(text, prompt)
        print(Fore.GREEN + "LLM Loaded! " + Fore.WHITE + "Start OpenAI generation...\r", end="")
        res = self.agent.run(text)
        print(Fore.GREEN + "LLM Generated!                                                    ")
        print(Fore.GREEN + "LLM Output : " + Fore.MAGENTA + res)
        return res
    

# Example
# audio = Audio(language="ja")
# audio.tts("こんにちは")
# res = audio.stt()
#                 # プロンプト                          # システムプロンプト
# res = audio.tts("タートボットさん、白色の紙袋を選びます","あなたは文章解析を行うAIです。入力された文字列の中から指定された紙袋の色を抽出し、その色のみを「必ず」配列で返してください。注意: 赤色ではなく赤という感じで色までは必要ありません。 例: 「Turtlebotさん、赤色の紙袋を選択します．」 -> [\"赤\"], 「Turtlebotさん、赤色の紙袋と青色の紙袋を選択します．」 -> [\"赤\", \"青\"], 「Turtlebotさん、赤色の紙袋と青色の紙袋と黄色の紙袋を選択します．」 -> [\"赤\", \"青\", \"黄\"]")
