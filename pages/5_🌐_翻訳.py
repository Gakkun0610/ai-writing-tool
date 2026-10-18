import streamlit as st

from utils.gemini_client import stream_generate
from utils.ui import MAX_CHARS_LONG, MAX_CHARS_SHORT, setup_page

setup_page("翻訳", "🌐")

st.caption("文章を指定した言語・トーンに翻訳します。")

LANGUAGES = ["英語", "日本語", "中国語（簡体字）", "中国語（繁体字）", "韓国語", "スペイン語", "フランス語", "ドイツ語"]

with st.form("translate_form"):
    text = st.text_area("翻訳したい文章*", max_chars=MAX_CHARS_LONG, height=250)
    col1, col2 = st.columns(2)
    with col1:
        target_lang = st.selectbox("翻訳先の言語", LANGUAGES)
    with col2:
        tone = st.selectbox("トーン", ["自然・標準", "フォーマル・ビジネス", "カジュアル・会話調"])
    context = st.text_input("文脈・用途（任意）", max_chars=MAX_CHARS_SHORT, placeholder="例：海外の取引先へのメールの一部")

    submitted = st.form_submit_button("翻訳する", type="primary", use_container_width=True)

if submitted:
    if not text.strip():
        st.error("翻訳したい文章を入力してください。")
    else:
        prompt_parts = [
            "あなたはプロの翻訳者です。以下の文章を翻訳してください。",
            f"# 翻訳先の言語\n{target_lang}",
            f"# トーン\n{tone}",
        ]
        if context.strip():
            prompt_parts.append(f"# 文脈・用途\n{context}")
        prompt_parts.append(f"# 原文\n{text}")
        prompt_parts.append("直訳ではなく、自然で読みやすい翻訳文のみを出力してください。")
        prompt = "\n\n".join(prompt_parts)

        st.subheader("翻訳結果")
        try:
            result = st.write_stream(
                stream_generate(prompt, model=st.session_state.model, temperature=st.session_state.temperature)
            )
            st.session_state["translate_result"] = result
        except RuntimeError as e:
            st.error(str(e))

if st.session_state.get("translate_result"):
    st.download_button(
        "テキストでダウンロード",
        st.session_state["translate_result"],
        file_name="translation.txt",
    )
