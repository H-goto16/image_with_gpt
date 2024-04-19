#!/usr/bin/python3

from g4f.client import Client
from g4f.Provider.GeminiPro import GeminiPro

from retry import retry

class imageWithGPT:

    MAX_TRY = 3
    DELAY = 1
    BACKOFF = 2

    @retry(Exception, tries=MAX_TRY, delay=DELAY, backoff=BACKOFF)
    def __init__(self, api_key):
        try:
            if not api_key:
                raise Exception("Please provide a valid API key")

            self.client = Client(
                api_key=api_key,
                provider=GeminiPro
            )
        except Exception as e:
            print(f"\033[31mInitialize Error Occurred! {str(e)}\nRestart initializing...\033[0m")
            raise Exception(f"An unknown error occurred: {e}")

    @retry(Exception, tries=MAX_TRY, delay=DELAY, backoff=BACKOFF)
    def get(self, prompt, image):
        try:
            res = self.client.chat.completions.create(
                model="gemini-pro-vision",
                messages=[{"role": "user", "content": prompt}],
                image=image,
            )
            return res.choices[0].message.content
        except Exception as e:
            print(f"\033[31mError Occurred! {str(e)}\nRestarting...\033[0m")
            raise Exception(f"An unknown error occurred: {e}")
