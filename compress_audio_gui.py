#!/usr/bin/env python3
"""音声ファイルを100MB以下に圧縮するGUIツール"""

import math
import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, ttk


# ─── 圧縮ロジック（compress_audio.py から流用） ───

def get_duration(filepath: str) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", filepath],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ファイルを読み取れません: {filepath}")
    return float(result.stdout.strip())


def get_file_size(filepath: str) -> int:
    return os.path.getsize(filepath)


def format_size(size_bytes: int) -> str:
    if size_bytes >= 1024 * 1024 * 1024:
        return f"{size_bytes / (1024**3):.1f} GB"
    if size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024**2):.1f} MB"
    return f"{size_bytes / 1024:.1f} KB"


def compress_audio(input_path: str, output_path: str, target_mb: float) -> dict:
    """圧縮を実行し、結果を dict で返す"""
    target_bytes = int(target_mb * 1024 * 1024)
    input_size = get_file_size(input_path)

    if input_size <= target_bytes:
        subprocess.run(["cp", input_path, output_path])
        return {
            "skipped": True,
            "input_size": input_size,
            "output_size": get_file_size(output_path),
            "output_path": output_path,
        }

    duration = get_duration(input_path)
    target_bitrate_kbps = math.floor((target_bytes * 8) / duration / 1000 * 0.95)
    if target_bitrate_kbps < 32:
        target_bitrate_kbps = 32

    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-vn", "-acodec", "aac",
        "-b:a", f"{target_bitrate_kbps}k",
        "-ar", "44100" if target_bitrate_kbps >= 64 else "22050",
        "-ac", "1" if target_bitrate_kbps < 64 else "2",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"圧縮に失敗しました:\n{result.stderr[:500]}")

    output_size = get_file_size(output_path)
    compression_ratio = (1 - output_size / input_size) * 100

    return {
        "skipped": False,
        "input_size": input_size,
        "output_size": output_size,
        "output_path": output_path,
        "duration": duration,
        "bitrate": target_bitrate_kbps,
        "ratio": compression_ratio,
    }


# ─── GUI ───

class AudioCompressorApp:
    BG = "#1e1e2e"
    FG = "#cdd6f4"
    ACCENT = "#89b4fa"
    ACCENT_HOVER = "#74c7ec"
    SUCCESS = "#a6e3a1"
    WARNING = "#f9e2af"
    SURFACE = "#313244"
    SUBTEXT = "#a6adc8"

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("音声圧縮ツール")
        self.root.geometry("520x580")
        self.root.configure(bg=self.BG)
        self.root.resizable(False, False)

        self.selected_file: str | None = None

        self._build_ui()

    # ── UI構築 ──

    def _build_ui(self):
        # タイトル
        tk.Label(
            self.root, text="🔊 音声圧縮ツール", font=("Helvetica", 20, "bold"),
            bg=self.BG, fg=self.FG,
        ).pack(pady=(20, 4))
        tk.Label(
            self.root, text="音声ファイルを指定サイズ以下に圧縮します",
            font=("Helvetica", 12), bg=self.BG, fg=self.SUBTEXT,
        ).pack(pady=(0, 16))

        # ファイル選択エリア
        self.drop_frame = tk.Frame(
            self.root, bg=self.SURFACE, highlightbackground=self.ACCENT,
            highlightthickness=2, cursor="hand2",
        )
        self.drop_frame.pack(padx=30, pady=(0, 12), fill="x", ipady=18)

        self.file_icon_label = tk.Label(
            self.drop_frame, text="📁", font=("Helvetica", 28),
            bg=self.SURFACE, fg=self.FG,
        )
        self.file_icon_label.pack(pady=(10, 2))

        self.file_label = tk.Label(
            self.drop_frame, text="クリックしてファイルを選択",
            font=("Helvetica", 13), bg=self.SURFACE, fg=self.SUBTEXT,
        )
        self.file_label.pack()

        self.file_info_label = tk.Label(
            self.drop_frame, text="対応形式: WAV, MP3, M4A",
            font=("Helvetica", 10), bg=self.SURFACE, fg=self.SUBTEXT,
        )
        self.file_info_label.pack(pady=(2, 8))

        for widget in (self.drop_frame, self.file_icon_label,
                       self.file_label, self.file_info_label):
            widget.bind("<Button-1>", lambda _: self._select_file())

        # 目標サイズ
        size_frame = tk.Frame(self.root, bg=self.BG)
        size_frame.pack(padx=30, fill="x", pady=(4, 0))

        tk.Label(
            size_frame, text="目標サイズ (MB):", font=("Helvetica", 12),
            bg=self.BG, fg=self.FG,
        ).pack(side="left")

        self.size_var = tk.StringVar(value="100")
        self.size_entry = tk.Entry(
            size_frame, textvariable=self.size_var, width=6,
            font=("Helvetica", 14), justify="center",
            bg=self.SURFACE, fg=self.FG, insertbackground=self.FG,
            relief="flat", highlightthickness=1,
            highlightbackground=self.ACCENT,
        )
        self.size_entry.pack(side="left", padx=(8, 0))

        # よく使うサイズのボタン
        presets_frame = tk.Frame(self.root, bg=self.BG)
        presets_frame.pack(padx=30, fill="x", pady=(8, 0))
        for label, val in [("25 MB", "25"), ("50 MB", "50"),
                           ("100 MB", "100"), ("200 MB", "200")]:
            btn = tk.Button(
                presets_frame, text=label, font=("Helvetica", 10),
                bg=self.SURFACE, fg=self.FG, activebackground=self.ACCENT,
                activeforeground=self.BG, relief="flat", padx=10, pady=4,
                command=lambda v=val: self.size_var.set(v),
            )
            btn.pack(side="left", padx=(0, 6))

        # 圧縮ボタン
        self.compress_btn = tk.Button(
            self.root, text="⚡ 圧縮する", font=("Helvetica", 16, "bold"),
            bg=self.ACCENT, fg=self.BG, activebackground=self.ACCENT_HOVER,
            activeforeground=self.BG, relief="flat", padx=20, pady=10,
            command=self._start_compress, state="disabled", cursor="hand2",
        )
        self.compress_btn.pack(pady=16)

        # プログレスバー
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor=self.SURFACE, background=self.ACCENT,
            thickness=8,
        )
        self.progress = ttk.Progressbar(
            self.root, style="Custom.Horizontal.TProgressbar",
            mode="indeterminate", length=460,
        )

        # 結果エリア
        self.result_frame = tk.Frame(self.root, bg=self.SURFACE)

        self.result_label = tk.Label(
            self.result_frame, text="", font=("Helvetica", 12),
            bg=self.SURFACE, fg=self.FG, justify="left", anchor="w",
        )
        self.result_label.pack(padx=16, pady=(12, 4), fill="x")

        self.finder_btn = tk.Button(
            self.result_frame, text="📂 Finderで開く", font=("Helvetica", 12),
            bg=self.ACCENT, fg=self.BG, activebackground=self.ACCENT_HOVER,
            relief="flat", padx=12, pady=6, cursor="hand2",
        )

    # ── ファイル選択 ──

    def _select_file(self):
        path = filedialog.askopenfilename(
            title="音声ファイルを選択",
            filetypes=[
                ("音声ファイル", "*.wav *.mp3 *.m4a *.aac *.ogg *.flac *.wma"),
                ("すべてのファイル", "*.*"),
            ],
        )
        if not path:
            return

        self.selected_file = path
        filename = os.path.basename(path)
        size = get_file_size(path)

        self.file_icon_label.config(text="🎵")
        self.file_label.config(text=filename, fg=self.FG)
        self.file_info_label.config(
            text=f"サイズ: {format_size(size)}",
            fg=self.SUBTEXT,
        )
        self.compress_btn.config(state="normal")

        # 結果エリアを隠す
        self.result_frame.pack_forget()
        self.progress.pack_forget()

    # ── 圧縮実行 ──

    def _start_compress(self):
        if not self.selected_file:
            return

        try:
            target_mb = float(self.size_var.get())
            if target_mb <= 0:
                raise ValueError
        except ValueError:
            self.result_label.config(
                text="⚠️ 目標サイズに正しい数値を入力してください", fg=self.WARNING,
            )
            self.result_frame.pack(padx=30, fill="x", pady=(0, 10))
            return

        # UI更新
        self.compress_btn.config(state="disabled", text="圧縮中...")
        self.progress.pack(padx=30, pady=(0, 8))
        self.progress.start(15)
        self.result_frame.pack_forget()

        # バックグラウンドスレッドで実行
        thread = threading.Thread(
            target=self._run_compress,
            args=(self.selected_file, target_mb),
            daemon=True,
        )
        thread.start()

    def _run_compress(self, input_path: str, target_mb: float):
        base, _ = os.path.splitext(input_path)
        output_path = f"{base}_compressed.m4a"

        try:
            result = compress_audio(input_path, output_path, target_mb)
            self.root.after(0, self._show_result, result)
        except Exception as e:
            self.root.after(0, self._show_error, str(e))

    def _show_result(self, result: dict):
        self.progress.stop()
        self.progress.pack_forget()
        self.compress_btn.config(state="normal", text="⚡ 圧縮する")

        if result["skipped"]:
            text = (
                f"✅ 既に目標サイズ以下です\n"
                f"サイズ: {format_size(result['input_size'])}"
            )
            self.result_label.config(text=text, fg=self.SUCCESS)
        else:
            text = (
                f"✅ 圧縮完了!\n"
                f"元サイズ:   {format_size(result['input_size'])}\n"
                f"出力サイズ: {format_size(result['output_size'])}\n"
                f"圧縮率:     {result['ratio']:.1f}%\n"
                f"ビットレート: {result['bitrate']} kbps"
            )
            self.result_label.config(text=text, fg=self.SUCCESS)

        self.result_frame.pack(padx=30, fill="x", pady=(0, 10))

        output_dir = os.path.dirname(result["output_path"])
        self.finder_btn.config(
            command=lambda: subprocess.run(["open", output_dir]),
        )
        self.finder_btn.pack(padx=16, pady=(4, 12))

    def _show_error(self, message: str):
        self.progress.stop()
        self.progress.pack_forget()
        self.compress_btn.config(state="normal", text="⚡ 圧縮する")

        self.result_label.config(text=f"❌ エラー\n{message}", fg=self.WARNING)
        self.result_frame.pack(padx=30, fill="x", pady=(0, 10))
        self.finder_btn.pack_forget()


def main():
    # ffmpegの存在確認
    if subprocess.run(["which", "ffmpeg"], capture_output=True).returncode != 0:
        root = tk.Tk()
        root.withdraw()
        tk.messagebox.showerror(
            "エラー",
            "ffmpegがインストールされていません。\n\n"
            "brew install ffmpeg\n\n"
            "でインストールしてください。",
        )
        sys.exit(1)

    root = tk.Tk()
    AudioCompressorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
