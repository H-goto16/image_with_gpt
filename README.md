# Online Audio Kit
シンプルな音声キット

**注意：インターネット環境が必要です。またAIを使用する場合はOpenAIのKeyの設定を必ず行って下さい。**

## 機能
+ Google APIを使用したシンプルな音声キット
+ 文字起こし、発話に対応
+ VOSKを用いた音声認識
+ 言語指定可能
+ OpenAIのLangChainを用いて高精度な文章解析

# インストール
```shell
pip install git+https://github.com/rionehome/online_audio_kit
```

# 使用方法
```python
from online_audio_kit import AudioKit

audio = AudioKit() # Option : AudioKit(language=str, open_api_key=str) 

recognized_text = audio.stt()

audio.tts("Hello! What drink do you like?")

llm_response = audio.llm("I like orange juice.", "You are an analytical AI.  Extract only your favorite drinks from the input text and output the names of the drinks as an array. Example, Human: I like orange juice but I don't like coffee. You: ['orange juice'], Human: My favorite drink is grape juice and apple juice. You: ['grape juice','apple juice']")

for text in audio.vosk()
  print(text)
  if (len(text) > 10):
    break
```

# セットアップ
+ .envファイルの入力
OpenAIから発行したAPIキーを入力
```sh:.env
OPENAI_API_KEY="xxxxxxxxxxxxxx" // 変更
```
+ .envを使用しない場合
インスタンスを生成するときに指定できます。
```python
audio = AudioKit(openai_api_key="YOUR API KEY")
```
