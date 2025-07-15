# 🔊 音声圧縮ツール / Audio Compressor

音声ファイルを指定サイズ（デフォルト100MB）以下に圧縮するツールです。
CLIとGUIデスクトップアプリの2種類を提供しています。

## 必要なもの

- Python 3.10+
- ffmpeg (`brew install ffmpeg`)

## 使い方

### GUI デスクトップアプリ

```bash
python3 compress_audio_gui.py
```

ファイル選択 → 目標サイズ設定 → 圧縮ボタンの3ステップで完了します。

### CLI

```bash
# 100MB以下に圧縮（デフォルト）
python3 compress_audio.py 音声ファイル.wav

# 目標サイズを指定
python3 compress_audio.py 音声ファイル.wav -s 50

# 出力ファイル名を指定
python3 compress_audio.py 音声ファイル.wav -o output.m4a
```

### macOS アプリ (.app) として使う

`compress_audio_gui.py` をmacOSアプリとして利用する場合は、以下の構造で `.app` バンドルを作成してください：

```
音声圧縮ツール.app/
  Contents/
    Info.plist
    MacOS/launch        ← python3でGUIスクリプトを起動するシェルスクリプト
    Resources/
      compress_audio_gui.py
```

## 対応フォーマット

- 入力: WAV, MP3, M4A, AAC, OGG, FLAC, WMA
- 出力: M4A (AAC)

## ライセンス

MIT
