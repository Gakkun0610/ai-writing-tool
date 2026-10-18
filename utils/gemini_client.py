"""Gemini API とのやり取りをまとめた薄いラッパー。

個人用ツールのため認証・DBは持たず、APIキーは
1. Streamlit の secrets (.streamlit/secrets.toml)
2. 環境変数 / .env
3. サイドバーでの直接入力 (st.session_state)
の優先順で読み込む。
"""

from __future__ import annotations

import os
from collections.abc import Iterator

import httpx
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

load_dotenv()

DEFAULT_MODEL = "gemini-3.8-flash"
# 1回の生成で使う出力トークンの上限。最長の「本格的（2500字程度）」の記事でも収まる量。
MAX_OUTPUT_TOKENS = 8192
# 無料枠で利用できるモデルのみ。Pro系（例: gemini-3.1-pro-preview）は有料のみのため含めない。
AVAILABLE_MODELS = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.5-flash-lite"]


def get_api_key() -> str | None:
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return os.environ.get("GEMINI_API_KEY") or st.session_state.get("gemini_api_key") or None


def is_ready() -> bool:
    return bool(get_api_key())


@st.cache_resource(show_spinner=False, max_entries=20, ttl=3600)
def _get_client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


def stream_generate(
    prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    system_instruction: str | None = None,
) -> Iterator[str]:
    """プロンプトを送り、テキストチャンクを順次 yield する。"""
    api_key = get_api_key()
    if not api_key:
        raise RuntimeError(
            "Gemini APIキーが設定されていません。サイドバーに入力するか、"
            ".env に GEMINI_API_KEY を設定してください。"
        )

    client = _get_client(api_key)
    config = types.GenerateContentConfig(
        temperature=temperature,
        system_instruction=system_instruction,
        max_output_tokens=MAX_OUTPUT_TOKENS,
    )

    try:
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=prompt,
            config=config,
        ):
            if chunk.text:
                yield chunk.text
    except errors.APIError as e:
        # 詳細（トレースバック等）は画面に出さず、各ページの except RuntimeError で表示させる
        raise RuntimeError(
            f"Gemini API でエラーが発生しました（コード: {e.code}）。"
            "APIキーや利用上限を確認し、時間をおいて再度お試しください。"
        ) from e
    except httpx.HTTPError as e:
        raise RuntimeError(
            "Gemini API に接続できませんでした。ネットワーク接続を確認し、時間をおいて再度お試しください。"
        ) from e
    except Exception as e:
        # 想定外の例外もトレースバックを画面に出さず、日本語メッセージに変換する（catch-all は必ず最後）
        raise RuntimeError(
            "予期しないエラーが発生しました。入力内容を確認し、時間をおいて再度お試しください。"
        ) from e
