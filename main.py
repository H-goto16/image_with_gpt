from dotenv import load_dotenv
import speech_recognition as sr
from gtts import gTTS
import os
from langchain.llms import OpenAI
from langchain.agents import initialize_agent
from langchain.chains.conversation.memory import ConversationBufferMemory
from os import environ
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1" 
import pygame

# Manual set API key, if you don't want to use .env file
# os.environ["OPENAI_API_KEY"] = ""

class Audio:
    def __init__(self, language="en"):
        self.recognizer = sr.Recognizer()
        self.language = language
        pygame.mixer.init()
        load_dotenv()

    def stt(self):
        with sr.Microphone() as source:
            print("\033[31mRECORDING..\033[0m")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)

        try:
            recognized_text = self.recognizer.recognize_google(audio, language=self.language)
            print(f"Recognized: {recognized_text}")
            return recognized_text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand the audio.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return None

    def tts(self, text):
        audio_path = "output.mp3"
        tts = gTTS(text=text, lang=self.language)
        tts.save(audio_path)
        
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
        os.remove(audio_path)
    
    def llm(self, text, prompt):
        self.llm=OpenAI()
        self.agent = initialize_agent(
            tools=[],
            llm=self.llm, 
            agent="conversational-react-description", 
            memory=ConversationBufferMemory(memory_key="chat_history"), 
        )
        self.agent.agent.llm_chain.prompt.template = prompt
        return self.agent.run(text)