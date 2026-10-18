import streamlit as st

from utils.gemini_client import stream_generate
from utils.ui import MAX_CHARS_LONG, MAX_CHARS_SHORT, setup_page

setup_page("ブログ記事作成", "📝")

st.caption("テーマや構成を指定すると、ブログ記事の下書きを生成します。")

with st.form("blog_form"):
    topic = st.text_input("記事のテーマ*", max_chars=MAX_CHARS_SHORT, placeholder="例：在宅ワークの生産性を上げる方法")
    keywords = st.text_input("含めたいキーワード（カンマ区切り、任意）", max_chars=MAX_CHARS_SHORT, placeholder="例：時間管理, 集中力, ツール")
    tone = st.selectbox(
        "文体・トーン",
        ["丁寧・フォーマル", "親しみやすい・カジュアル", "専門的・データ重視", "熱意を感じる・エモーショナル"],
    )
    length = st.select_slider(
        "記事のボリューム",
        options=["短め（400字程度）", "標準（800字程度）", "長め（1500字程度）", "本格的（2500字程度）"],
        value="標準（800字程度）",
    )
    outline = st.text_area("構成の希望（見出し案など、任意）", max_chars=MAX_CHARS_LONG, placeholder="例：導入→原因→解決策3つ→まとめ")
    audience = st.text_input("想定読者（任意）", max_chars=MAX_CHARS_SHORT, placeholder="例：在宅勤務を始めたばかりの20代会社員")

    submitted = st.form_submit_button("記事を生成", type="primary", use_container_width=True)

if submitted:
    if not topic.strip():
        st.error("記事のテーマを入力してください。")
    else:
        prompt_parts = [
            "あなたはプロのブログライターです。以下の条件でブログ記事を執筆してください。",
            f"# テーマ\n{topic}",
            f"# 文体・トーン\n{tone}",
            f"# ボリューム\n{length}",
        ]
        if keywords.strip():
            prompt_parts.append(f"# 含めたいキーワード\n{keywords}")
        if audience.strip():
            prompt_parts.append(f"# 想定読者\n{audience}")
        if outline.strip():
            prompt_parts.append(f"# 構成の希望\n{outline}")
        prompt_parts.append(
            "見出し（##）を使って読みやすく構成し、Markdown形式で出力してください。"
            "冒頭に読者の関心を引く導入、最後にまとめを入れてください。"
        )
        prompt = "\n\n".join(prompt_parts)

        st.subheader("生成結果")
        try:
            result = st.write_stream(
                stream_generate(prompt, model=st.session_state.model, temperature=st.session_state.temperature)
            )
            st.session_state["blog_result"] = result
        except RuntimeError as e:
            st.error(str(e))

if st.session_state.get("blog_result"):
    st.download_button(
        "Markdownでダウンロード",
        st.session_state["blog_result"],
        file_name="blog_article.md",
        mime="text/markdown",
    )
