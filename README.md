# Online Audio Kit

**注意：インターネット環境が必要です。**

## 機能
+ Google APIを使用したシンプルな音声キット
+ 文字起こし、発話に対応
+ 言語指定可能
+ OpenAIのLangChainを用いて超高精度な文章解析

## 環境構築
+ パッケージインストール
```
pip install -r requirements.txt
```
+ .envファイルの入力
OpenAIから発行したAPIキーを入力
```sh:.env
OPENAI_API_KEY="xxxxxxxxxxxxxx" // 変更
```
## 使用方法

```python:example.py
from path.to.main import Audio

# インスタンス作成
audio = Audio()
# 文字起こし
text = audio.stt()
# 発話
audio.tts("発話させる文章")
# LLM解析
res = audio.llm("解析したい文章", "システムプロンプト")
```

以下のようにすることで言語を指定できます。
```python
audio = Audio(language="ja")
```