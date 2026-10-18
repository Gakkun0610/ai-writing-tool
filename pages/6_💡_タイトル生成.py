import streamlit as st

from utils.gemini_client import stream_generate
from utils.ui import MAX_CHARS_LONG, setup_page

setup_page("タイトル・見出し生成", "💡")

st.caption("記事の内容やテーマから、複数のタイトル案を生成します。")

with st.form("title_form"):
    content = st.text_area(
        "記事の内容・テーマ*",
        max_chars=MAX_CHARS_LONG,
        height=200,
        placeholder="記事の要約、本文、もしくはテーマを入力してください",
    )
    num = st.slider("生成するタイトル案の数", 3, 15, 8)
    styles = st.multiselect(
        "重視したいスタイル（複数選択可・任意）",
        ["SEOを意識", "好奇心を刺激する", "数字を入れる", "疑問形にする", "ベネフィットを強調", "簡潔・端的"],
        default=["SEOを意識", "好奇心を刺激する", "数字を入れる"],
    )

    submitted = st.form_submit_button("タイトル案を生成", type="primary", use_container_width=True)

if submitted:
    if not content.strip():
        st.error("記事の内容・テーマを入力してください。")
    else:
        prompt_parts = [
            "あなたは読まれるタイトルを作るのが得意な編集者です。",
            f"以下の内容に基づいて、タイトル案を{num}個、番号付きリストで提案してください。",
        ]
        if styles:
            prompt_parts.append(f"# 重視したいスタイル\n{', '.join(styles)}")
        prompt_parts.append(f"# 記事の内容・テーマ\n{content}")
        prompt_parts.append("それぞれのタイトルの後に、狙いを一言で添えてください。")
        prompt = "\n\n".join(prompt_parts)

        st.subheader("タイトル案")
        try:
            result = st.write_stream(
                stream_generate(prompt, model=st.session_state.model, temperature=st.session_state.temperature)
            )
            st.session_state["title_result"] = result
        except RuntimeError as e:
            st.error(str(e))

if st.session_state.get("title_result"):
    st.download_button(
        "テキストでダウンロード",
        st.session_state["title_result"],
        file_name="titles.txt",
    )
