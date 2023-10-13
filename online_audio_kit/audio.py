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

    #### 注意: OpenAIのKeyは.envに記述するか、インスタンス化時にopenai_api_key引数に渡してください。
    `.env`例
    ```.env
    OPENAI_API_KEY="xxxxxxxxxxxxxxxxxxx"
    ```

    + 引数:\n
    language (Literal["ja", "en"]): 音声認識や音声合成に使用する言語を指定します。デフォルトは"en"です。"en"はVOSKではen-usに変換されます。ただしGoogleのAPIへは"en"で渡します。\n
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
        model_name = "en-us" if language == "en" else language
        print("Audio module loading... ("+ model_name +")\r", end="")
        try:
            init(autoreset=True)
            self.recognizer = sr.Recognizer()
            self.language = language
            self.openai_api_key = openai_api_key
            SetLogLevel(-1)
            self.model = Model(lang=model_name)
            pygame.mixer.init()
            if self.openai_api_key:
                os.environ["OPENAI_API_KEY"] = self.openai_api_key
            load_dotenv()
        except Exception as e:
            print(f"\033[31mInitialize Error Occurred! {str(e)}\nRestart initializing...\033[0m")
            raise Exception(f"An unknown error occurred: {e}")
        else:
            print(Fore.GREEN + "Audio module loaded! ("+ model_name +")" + " " * 20 )
            if not self.openai_api_key:
                print(Fore.YELLOW + "OpenAI API Key is not set. Please set OPENAI_API_KEY in .env or pass it to the constructor.\nYou can't use LLM function.")

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
        print(Fore.CYAN + "VOSK Preparing...("+ self.language +")\r", end="")
        q = queue.Queue()

        def callback(indata, frames, time, status):
            """This is called (from a separate thread) for each audio block."""
            if status:
                print(status, file=sys.stderr)
            q.put(bytes(indata))

        try:
            device_info = sd.query_devices(None, "input")
            samplerate = int(device_info["default_samplerate"])

            with sd.RawInputStream(samplerate=samplerate, blocksize = 8000,
                    dtype="int16", channels=1, callback=callback):

                print(Fore.GREEN + "VOSK Loaded! Start VOSK recognition...")
                rec = KaldiRecognizer(self.model, samplerate)
                while True:
                    data = q.get()
                    if rec.AcceptWaveform(data):
                        final = loads(rec.Result())["text"]
                        print(Fore.GREEN + "Recognized: " + Fore.WHITE + final)
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
    def play(self, audio_path):
        """
        音声ファイルを再生するメソッド\n

        引数:
            audio_path (str): 再生する音声ファイルのパス
        return:
            None
        """
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            print(Fore.GREEN + "Start Playing...\r", end="")
            continue

    @retry(exceptions=Exception, tries=MAX_TRY, delay=DELAY, backoff=BACKOFF)
    def tts(self, text, mode = "default", path = "output.mp3"):
        """
        GoogleのTTSを使用して音声合成を行うメソッド\n
        生成された音声を再生します。\n

        引数:
            text (str): 合成する文章
            mode (str): モード (default: 生成->再生->削除, gen: 生成のみ)
        return:
            None
        """
        print(Fore.CYAN + "TTS Loading...                     \r", end="")
        try:
            tts = gTTS(text=text, lang=self.language)
            tts.save(path)
            print(Fore.CYAN + "TTS Loaded!\r", end="")
            if (mode == "default"):
                self.play(path)
        except Exception as e:
            print(Fore.RED + f"An unknown error occurred: {e}")
            raise Exception(f"An unknown error occurred: {e}")
        if (mode == "default"):
            print(Fore.GREEN + "TTS Played! removing audio file...\r", end="")
            os.remove(path)

    @retry(exceptions=Exception, tries=MAX_TRY, delay=DELAY, backoff=BACKOFF)
    def llm(self, text, prompt):
        """
        OpenAI APIを使用して文章解析を行うメソッド\n
        解析結果を返します。\n

        引数:
            text (str): 解析する文章
            prompt (str): 解析に使用するprompt
        return:
            str | int: 解析結果 or Errorのとき1を返す

        使用方法:
        ```python
        audio = AudioKit()
        res = audio.llm("Hello, my name is John.", "You are a very high-performance voice analysis AI. Extract only the food from the input text.")
        print(res)
        ```
        """
        print(Fore.WHITE + "LLM Loading...\r", end="")
        if not self.openai_api_key:
            print(Fore.RED + "API KEY DOES NOT EXITS. EXITING...")
            return 1
        try:
            self.llm = OpenAI()
            self.agent = initialize_agent(
                tools=[],
                llm=self.llm,
                agent="conversational-react-description",
                agent_kwargs={
                    "prefix": prompt
                }
            )
            print(Fore.GREEN + "LLM Loaded! " + Fore.WHITE + "Start OpenAI generation...\r", end="")
            res = self.agent.run(text)
        except Exception as e:
            print(Fore.RED + f"An unknown error occurred: {e}")
            raise Exception(f"An unknown error occurred: {e}")
        print(Fore.GREEN + "LLM Generated!                                                    ")
        print(Fore.GREEN + "LLM Output : " + Fore.MAGENTA + res)
        return res