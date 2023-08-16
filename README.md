# Online Audio Kit
シンプルな音声キット

**注意：インターネット環境が必要です。**

## 機能
+ Google APIを使用したシンプルな音声キット
+ 文字起こし、発話に対応
+ 言語指定可能
+ OpenAIのLangChainを用いて超高精度な文章解析

# インストール
```shell
pip install git+https://github.com/rionehome/online_audio_kit
```

# 使用方法
```python
from online_audio_kit import AudioKit
audio = AudioKit() # Option : AudioKit(language=str, stt_publish=bool, min=int, max_try=int, open_api_key=str) 

recognized_text = audio.stt()
audio.tts("Hello!")
llm_response = audio.llm("I like orange juice.", "You are analyze AI. You must .....")

# Testing now
audio.vosk()
```

# 環境構築
+ .envファイルの入力
OpenAIから発行したAPIキーを入力
```sh:.env
OPENAI_API_KEY="xxxxxxxxxxxxxx" // 変更
```
+ .envを使用しない場合
インスタンスを生成するときに指定できます。
```python
audio = Audio(openai_api_key="YOUR API KEY")
```

