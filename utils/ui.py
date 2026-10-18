"""各ページ共通のセットアップ（ページ設定・サイドバー）。"""

from __future__ import annotations

import hmac
import os

import streamlit as st

from utils.gemini_client import AVAILABLE_MODELS, DEFAULT_MODEL, is_ready

# 入力欄の文字数上限（入力トークン料金の上限を決める）
MAX_CHARS_LONG = 20000
MAX_CHARS_SHORT = 500


def setup_page(title: str, icon: str) -> None:
    st.set_page_config(page_title=f"{title} | AI Writing Tool", page_icon=icon, layout="wide")
    if not _check_password():
        st.stop()
    _render_sidebar()
    st.title(f"{icon} {title}")


def _check_password() -> bool:
    """secrets に APP_PASSWORD があるときだけパスワードを要求する（未設定のローカル環境ではスキップ）。"""
    try:
        expected = st.secrets["APP_PASSWORD"]
    except Exception:
        return True
    if st.session_state.get("authenticated"):
        return True

    st.title("🔒 AI Writing Tool")
    pw = st.text_input("パスワード", type="password")
    if pw and hmac.compare_digest(pw.encode(), str(expected).encode()):
        st.session_state["authenticated"] = True
        st.rerun()
    elif pw:
        st.error("パスワードが違います。")
    return False


def _render_sidebar() -> None:
    with st.sidebar:
        st.header("⚙️ 設定")

        st.session_state.setdefault("gemini_api_key", "")
        if os.environ.get("GEMINI_API_KEY") or _has_secret_key():
            st.success("APIキーは環境変数 / secrets から読み込まれています。")
        else:
            st.session_state.gemini_api_key = st.text_input(
                "Gemini APIキー",
                value=st.session_state.gemini_api_key,
                type="password",
                help="環境変数 GEMINI_API_KEY が未設定の場合はここに入力してください。",
            )
            if not st.session_state.gemini_api_key:
                st.warning("APIキーが未設定です。")

        st.session_state.setdefault("model", DEFAULT_MODEL)
        st.session_state.model = st.selectbox(
            "モデル",
            AVAILABLE_MODELS,
            index=AVAILABLE_MODELS.index(st.session_state.model)
            if st.session_state.model in AVAILABLE_MODELS
            else 0,
            help="いずれも無料枠で利用可能。flash-lite: 最速・最軽量 / flash: バランス型 / 3.7-flash: やや高精度",
        )

        st.session_state.setdefault("temperature", 0.7)
        st.session_state.temperature = st.slider(
            "創造性 (temperature)", 0.0, 1.5, st.session_state.temperature, 0.1
        )

        st.divider()
        st.caption(
            "個人用ツールのためデータは保存されません（このセッション内のみ保持）。"
            "入力内容は Google Gemini API に送信されます。個人情報・機密情報は入力しないでください。"
        )


def _has_secret_key() -> bool:
    try:
        return "GEMINI_API_KEY" in st.secrets
    except Exception:
        return False
