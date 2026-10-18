import streamlit as st

from utils.gemini_client import stream_generate
from utils.ui import MAX_CHARS_LONG, MAX_CHARS_SHORT, setup_page

setup_page("文章要約", "📄")

st.caption("長い文章を貼り付けると、指定した形式・長さで要約します。")

with st.form("summary_form"):
    text = st.text_area("要約したい文章*", max_chars=MAX_CHARS_LONG, height=300, placeholder="ここに長文を貼り付けてください")
    style = st.selectbox("要約の形式", ["箇条書き", "一段落の文章", "見出し付きの構造化サマリー"])
    length = st.select_slider(
        "要約の長さ",
        options=["とても短く（1〜2行）", "短め（3〜5行）", "標準（全体の1/3程度）", "詳しめ（全体の半分程度）"],
        value="短め（3〜5行）",
    )
    focus = st.text_input("特に重視したい観点（任意）", max_chars=MAX_CHARS_SHORT, placeholder="例：結論と数値データを中心に")

    submitted = st.form_submit_button("要約を生成", type="primary", use_container_width=True)

if submitted:
    if not text.strip():
        st.error("要約したい文章を入力してください。")
    else:
        prompt_parts = [
            "あなたは要約が得意な編集者です。以下の文章を指定条件に沿って要約してください。",
            f"# 要約形式\n{style}",
            f"# 要約の長さ\n{length}",
        ]
        if focus.strip():
            prompt_parts.append(f"# 重視したい観点\n{focus}")
        prompt_parts.append(f"# 要約対象の文章\n{text}")
        prompt_parts.append("元の文章にない情報を付け加えず、事実に忠実に要約してください。")
        prompt = "\n\n".join(prompt_parts)

        st.subheader("要約結果")
        try:
            result = st.write_stream(
                stream_generate(prompt, model=st.session_state.model, temperature=st.session_state.temperature)
            )
            st.session_state["summary_result"] = result
        except RuntimeError as e:
            st.error(str(e))

if st.session_state.get("summary_result"):
    st.download_button(
        "テキストでダウンロード",
        st.session_state["summary_result"],
        file_name="summary.txt",
    )
