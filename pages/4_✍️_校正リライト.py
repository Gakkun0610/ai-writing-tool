import streamlit as st

from utils.gemini_client import stream_generate
from utils.ui import MAX_CHARS_LONG, MAX_CHARS_SHORT, setup_page

setup_page("校正・リライト", "✍️")

st.caption("文章の誤字脱字チェックや、トーン・文体の変換を行います。")

ACTIONS = {
    "誤字脱字・文法チェック": "誤字脱字、文法的な誤り、不自然な言い回しを修正してください。修正箇所とその理由も簡潔にリストアップしてください。",
    "より自然な日本語に": "不自然だったり、機械的だったりする表現を、自然で読みやすい日本語に書き直してください。",
    "フォーマルに変換": "ビジネスシーンにふさわしい、丁寧でフォーマルな文体に書き直してください。",
    "カジュアルに変換": "親しみやすく、カジュアルな口語調の文体に書き直してください。",
    "簡潔に短縮": "意味を保ったまま、できるだけ簡潔で無駄のない文章に書き直してください。",
    "丁寧・敬語を強化": "敬語表現を適切に使い、より丁寧な印象になるよう書き直してください。",
}

with st.form("rewrite_form"):
    text = st.text_area("対象の文章*", max_chars=MAX_CHARS_LONG, height=250, placeholder="校正・リライトしたい文章を入力してください")
    action = st.selectbox("実行したい処理", list(ACTIONS.keys()))
    extra = st.text_input("追加の指示（任意）", max_chars=MAX_CHARS_SHORT, placeholder="例：専門用語はそのまま残してほしい")

    submitted = st.form_submit_button("実行", type="primary", use_container_width=True)

if submitted:
    if not text.strip():
        st.error("対象の文章を入力してください。")
    else:
        prompt_parts = [
            "あなたは日本語の校正・編集のプロフェッショナルです。",
            f"# 指示\n{ACTIONS[action]}",
        ]
        if extra.strip():
            prompt_parts.append(f"# 追加の指示\n{extra}")
        prompt_parts.append(f"# 対象の文章\n{text}")
        prompt_parts.append("修正後の文章を提示し、その後に主な変更点を簡潔に箇条書きで説明してください。")
        prompt = "\n\n".join(prompt_parts)

        st.subheader("結果")
        try:
            result = st.write_stream(
                stream_generate(prompt, model=st.session_state.model, temperature=st.session_state.temperature)
            )
            st.session_state["rewrite_result"] = result
        except RuntimeError as e:
            st.error(str(e))

if st.session_state.get("rewrite_result"):
    st.download_button(
        "テキストでダウンロード",
        st.session_state["rewrite_result"],
        file_name="rewrite.txt",
    )
