#!/usr/bin/python3

from g4f.client import Client
from g4f.Provider.GeminiPro import GeminiPro

class imageWithGPT:
    def __init__(self, api_key):
        self.client = Client(
            api_key=api_key,
            provider=GeminiPro
        )

    def get(self, prompt, image):
        res = self.client.chat.completions.create(
            model="gemini-pro-vision",
            messages=[{"role": "user", "content": prompt}],
            image=image,
        )
        return res.choices[0].message.context

