from dotenv import load_dotenv
import speech_recognition as sr
from gtts import gTTS
import os
from langchain.llms import OpenAI
from langchain.agents import initialize_agent
from langchain.chains.conversation.memory import ConversationBufferMemory
from colorama import init
from retry import retry
from colorama import Fore, Back
import argparse
import queue
import sys
import sounddevice as sd
from json import loads
from vosk import Model, KaldiRecognizer, SetLogLevel
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1" 
import pygame

class AudioKit:
    """
    # Online Audio Kit
    音声エンジンを提供するクラスです。\n
    このクラスをインスタンス化することで、音声認識や音声合成、文章解析を行うことができます。\n

    + 引数:\n
    language (str): 音声認識や音声合成に使用する言語を指定します。デフォルトは"en"です。\n
    openai_api_key (str): OpenAI APIキーを指定します。デフォルトはNoneです。\n

    + クラス変数:\n
    MAX_TRY (int): エラーが発生した際にリトライする最大回数を指定します。デフォルトは3です。\n
    DELAY (int): リトライする際の待機時間を指定します。デフォルトは1です。\n
    BACKOFF (int): リトライする際の待機時間の増加量を指定します。デフォルトは2です。\n
    """

    MAX_TRY = 3
    DELAY = 1
    BACKOFF = 2
    
    @retry(exceptions=Exception, tries=MAX_TRY, delay=DELAY, backoff=BACKOFF)
    def __init__(self, language="en", openai_api_key=None):
        print("Audio module loading...\r", end="")
        try:
            init(autoreset=True)
            self.recognizer = sr.Recognizer()
            self.language = language
            SetLogLevel(-1)
            self.model = Model(lang=self.language)
            pygame.mixer.init()

            if openai_api_key:
                os.environ["OPENAI_API_KEY"] = openai_api_key
            load_dotenv()
        except Exception as e:
            print(f"\033[31mInitialize Error Occurred! {str(e)}\nRestart initializing...\033[0m")
            raise Exception(f"An unknown error occurred: {e}")
        else:
            print(Fore.GREEN + "Audio module loaded!   ")

    @retry(exceptions=Exception, tries=MAX_TRY, delay=DELAY, backoff=BACKOFF)
    def vosk(self):
        """
        VOSKの音声認識を行うメソッド\n
        ジェネレーターを返すので、for文などで回すことで認識結果を取得できます。\n
        必要に応じてROSへのパブリッシュなどを行ってください。

        引数:
            None
        yield:
            str: 認識結果

        使用方法:
        ```python
        audio = AudioKit()
        for result in audio.vosk():
            print(result)
        ```
        """
        print(Fore.CYAN + "VOSK Preparing...\r", end="")
        q = queue.Queue()

        def int_or_str(text):
            """Helper function for argument parsing."""
            try:
                return int(text)
            except ValueError:
                return text

        def callback(indata, frames, time, status):
            """This is called (from a separate thread) for each audio block."""
            if status:
                print(status, file=sys.stderr)
            q.put(bytes(indata))

        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument(
            "-l", "--list-devices", action="store_true",
            help="show list of audio devices and exit")
        args, remaining = parser.parse_known_args()
        if args.list_devices:
            print(sd.query_devices())
            parser.exit(0)
        parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            parents=[parser])
        parser.add_argument(
            "-f", "--filename", type=str, metavar="FILENAME",
            help="audio file to store recording to")
        parser.add_argument(
            "-d", "--device", type=int_or_str,
            help="input device (numeric ID or substring)")
        parser.add_argument(
            "-r", "--samplerate", type=int, help="sampling rate")
        parser.add_argument(
            "-m", "--model", type=str, help="language model; e.g. en-us, fr, nl; default is en-us")
        args = parser.parse_args(remaining)

        try:
            if args.samplerate is None:
                device_info = sd.query_devices(args.device, "input")
                args.samplerate = int(device_info["default_samplerate"])
                
            if args.model is None:
                model = self.model
            else:
                model = Model(lang=args.model)

            with sd.RawInputStream(samplerate=args.samplerate, blocksize = 8000, device=args.device,
                    dtype="int16", channels=1, callback=callback):

                print(Fore.GREEN + "VOSK Loaded! Start VOSK recognition...")
                rec = KaldiRecognizer(model, args.samplerate)
                while True:
                    data = q.get()
                    if rec.AcceptWaveform(data):
                        final = loads(rec.Result())["text"]
                        print(Fore.GREEN + "Recognized: " + Fore.WHITE + final)
                        if len(final) > self.min:
                            yield final
                    else:
                        partial = loads(rec.PartialResult())["partial"]
                        print(Fore.CYAN + "Partial:    " + Fore.WHITE + partial)
                        yield partial

        except Exception as e:
            raise Exception(f"An unknown error occurred: {e}")
    
    @retry(exceptions=Exception, tries=MAX_TRY, delay=DELAY, backoff=BACKOFF)
    def stt(self):
        """
        Google SpeechRecognition APIを使用して音声認識を行うメソッド\n
        認識結果を返します。\n

        引数:
            None
        return:
            str: 認識結果
        """
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
            raise sr.UnknownValueError("Google Speech Recognition could not understand the audio.")
        except sr.RequestError as e:
            print(Fore.RED + f"Could not request results from Google Speech Recognition service; {e}")
            raise sr.RequestError(f"Could not request results from Google Speech Recognition service; {e}")
        except Exception as e:
            print(Fore.RED + f"An unknown error occurred: {e}")
            raise Exception(f"An unknown error occurred: {e}")

    @retry(exceptions=Exception, tries=MAX_TRY, delay=DELAY, backoff=BACKOFF)
    def tts(self, text):
        """
        GoogleのTTSを使用して音声合成を行うメソッド\n
        生成された音声を再生します。\n
        
        引数:
            text (str): 合成する文章
        return:
            None
        """
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
            print(Fore.RED + f"An unknown error occurred: {e}")
            raise Exception(f"An unknown error occurred: {e}")
        print(Fore.GREEN + "TTS Played! removing audio file...\r", end="")
        os.remove(audio_path)

    @retry(exceptions=Exception, tries=MAX_TRY, delay=DELAY, backoff=BACKOFF)
    def llm(self, text, prompt):
        """
        OpenAI APIを使用して文章解析を行うメソッド\n
        解析結果を返します。\n

        引数:
            text (str): 解析する文章
            prompt (str): 解析に使用するprompt
        return:
            str: 解析結果

        使用方法:
        ```python   
        audio = AudioKit()
        res = audio.llm("Hello, my name is John.", "You are a very high-performance voice analysis AI. Extract only the food from the input text.")
        print(res)
        ```
        """
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
            print(Fore.GREEN + "LLM Loaded! " + Fore.WHITE + "Start OpenAI generation...\r", end="")
            res = self.agent.run(text)
        except Exception as e:
            print(Fore.RED + f"An unknown error occurred: {e}")
            raise Exception("An unknown error occurred: {e}")
        print(Fore.GREEN + "LLM Generated!                                                    ")
        print(Fore.GREEN + "LLM Output : " + Fore.MAGENTA + res)
        return res