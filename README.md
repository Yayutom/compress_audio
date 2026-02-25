# 🔊 音声圧縮ツール

音声ファイルを指定サイズ（デフォルト100MB）以下に圧縮するツールです。

## 初回セットアップ（Mac）

初めて使う方は、以下の3ステップで準備してください。

### ステップ1: Homebrewをインストール

「ターミナル」アプリを開いて（Spotlight で「ターミナル」と検索）、以下をコピー＆ペーストして Enter を押してください。

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

※ 途中でMacのパスワードを聞かれたら入力してください（入力中は画面に表示されません）

### ステップ2: ffmpegをインストール

同じくターミナルで以下を実行してください。

```
brew install ffmpeg
```

### ステップ3: このツールをダウンロード

ターミナルで以下を実行してください。

```
cd ~/Desktop
git clone https://github.com/Yayutom/compress_audio.git
```

デスクトップに `compress_audio` フォルダが作られます。

## 使い方

### GUIアプリ（おすすめ）

ターミナルで以下を実行すると、ウィンドウが開きます。

```
python3 ~/Desktop/compress_audio/compress_audio_gui.py
```

1. 画面をクリックして音声ファイルを選択
2. 目標サイズを設定（デフォルト100MB）
3. 「⚡ 圧縮する」ボタンを押す
4. 完了後「📂 Finderで開く」で出力ファイルを確認

圧縮されたファイルは元のファイルと同じフォルダに `〇〇_compressed.m4a` として保存されます。

### コマンドライン（上級者向け）

```bash
# 100MB以下に圧縮
python3 ~/Desktop/compress_audio/compress_audio.py 音声ファイル.wav

# 50MB以下に圧縮
python3 ~/Desktop/compress_audio/compress_audio.py 音声ファイル.wav -s 50

# 出力ファイル名を指定
python3 ~/Desktop/compress_audio/compress_audio.py 音声ファイル.wav -o output.m4a
```

## 対応フォーマット

- 入力: WAV, MP3, M4A, AAC, OGG, FLAC, WMA
- 出力: M4A (AAC)

## ライセンス

MIT
