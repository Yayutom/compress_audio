#!/usr/bin/env python3
"""音声ファイルを100MB以下に圧縮するツール"""

import argparse
import math
import os
import subprocess
import sys

TARGET_SIZE_MB = 100
TARGET_SIZE_BYTES = TARGET_SIZE_MB * 1024 * 1024


def get_duration(filepath: str) -> float:
    """音声ファイルの長さ（秒）を取得"""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", filepath],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"エラー: ファイルを読み取れません: {filepath}", file=sys.stderr)
        sys.exit(1)
    return float(result.stdout.strip())


def get_file_size(filepath: str) -> int:
    return os.path.getsize(filepath)


def format_size(size_bytes: int) -> str:
    if size_bytes >= 1024 * 1024 * 1024:
        return f"{size_bytes / (1024**3):.1f} GB"
    if size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024**2):.1f} MB"
    return f"{size_bytes / 1024:.1f} KB"


def compress_audio(input_path: str, output_path: str, target_mb: float) -> None:
    target_bytes = int(target_mb * 1024 * 1024)
    input_size = get_file_size(input_path)

    print(f"入力ファイル: {input_path}")
    print(f"現在のサイズ: {format_size(input_size)}")
    print(f"目標サイズ:   {target_mb} MB 以下")

    if input_size <= target_bytes:
        print(f"\n既に {target_mb} MB 以下です。コピーします。")
        subprocess.run(["cp", input_path, output_path])
        return

    duration = get_duration(input_path)
    print(f"長さ:         {duration:.1f} 秒 ({duration/60:.1f} 分)")

    # 目標ビットレートを計算（kbps）。マージン5%確保
    target_bitrate_kbps = math.floor((target_bytes * 8) / duration / 1000 * 0.95)

    # 最低32kbps（それ以下は品質が著しく低下）
    if target_bitrate_kbps < 32:
        print(f"\n警告: 必要ビットレートが {target_bitrate_kbps} kbps と非常に低いです。")
        print("品質が大幅に低下する可能性があります。")
        target_bitrate_kbps = 32

    print(f"圧縮ビットレート: {target_bitrate_kbps} kbps")
    print(f"\n圧縮中...")

    # AAC形式（.m4a）で圧縮。高品質かつ高圧縮率
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-vn",  # 映像を除外
        "-acodec", "aac",
        "-b:a", f"{target_bitrate_kbps}k",
        "-ar", "44100" if target_bitrate_kbps >= 64 else "22050",
        "-ac", "1" if target_bitrate_kbps < 64 else "2",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"エラー: 圧縮に失敗しました", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(1)

    output_size = get_file_size(output_path)
    compression_ratio = (1 - output_size / input_size) * 100

    print(f"\n完了!")
    print(f"出力ファイル: {output_path}")
    print(f"出力サイズ:   {format_size(output_size)}")
    print(f"圧縮率:       {compression_ratio:.1f}%")

    if output_size > target_bytes:
        print(f"\n警告: 目標サイズを超えています。より低いビットレートで再試行してください。")


def main():
    parser = argparse.ArgumentParser(
        description="音声ファイルを指定サイズ以下に圧縮します（デフォルト: 100MB）"
    )
    parser.add_argument("input", help="入力音声ファイル（WAV, MP3, M4A等）")
    parser.add_argument("-o", "--output", help="出力ファイルパス（省略時は自動生成）")
    parser.add_argument(
        "-s", "--size", type=float, default=TARGET_SIZE_MB,
        help=f"目標サイズ（MB単位、デフォルト: {TARGET_SIZE_MB}）"
    )
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"エラー: ファイルが見つかりません: {args.input}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        output_path = args.output
    else:
        base, _ = os.path.splitext(args.input)
        output_path = f"{base}_compressed.m4a"

    compress_audio(args.input, output_path, args.size)


if __name__ == "__main__":
    main()
