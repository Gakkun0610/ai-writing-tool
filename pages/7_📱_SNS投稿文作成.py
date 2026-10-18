import streamlit as st

from utils.gemini_client import stream_generate
from utils.ui import MAX_CHARS_LONG, setup_page

setup_page("SNS投稿文作成", "📱")

st.caption("プラットフォームに合わせたSNS投稿文を作成します。")

PLATFORM_HINTS = {
    "X（Twitter）": "140字前後を目安に、簡潔でインパクトのある文にしてください。",
    "Instagram": "改行を活かした読みやすいキャプションにしてください。絵文字を適度に使ってください。",
    "Facebook": "やや丁寧で説明的な文体にしてください。",
    "LinkedIn": "ビジネス・プロフェッショナル向けの文体にしてください。",
    "note / ブログ告知": "記事への興味を引く、少し長めの紹介文にしてください。",
}

with st.form("sns_form"):
    topic = st.text_area("投稿したい内容*", max_chars=MAX_CHARS_LONG, height=150, placeholder="例：新しくリリースしたアプリの機能紹介")
    platform = st.selectbox("プラットフォーム", list(PLATFORM_HINTS.keys()))
    tone = st.selectbox("トーン", ["親しみやすい", "熱意を感じる", "落ち着いた・信頼感重視", "ユーモアを交える"])
    use_hashtags = st.checkbox("ハッシュタグ案も提案する", value=True)
    num_variations = st.slider("パターン数", 1, 5, 3)

    submitted = st.form_submit_button("投稿文を生成", type="primary", use_container_width=True)

if submitted:
    if not topic.strip():
        st.error("投稿したい内容を入力してください。")
    else:
        prompt_parts = [
            "あなたはSNSマーケティングが得意なコピーライターです。",
            f"# プラットフォーム\n{platform}\n{PLATFORM_HINTS[platform]}",
            f"# トーン\n{tone}",
            f"# 投稿したい内容\n{topic}",
            f"異なる切り口で{num_variations}パターンの投稿文を作成してください。",
        ]
        if use_hashtags:
            prompt_parts.append("各パターンの最後に、関連するハッシュタグ案を3〜5個添えてください。")
        prompt = "\n\n".join(prompt_parts)

        st.subheader("生成結果")
        try:
            result = st.write_stream(
                stream_generate(prompt, model=st.session_state.model, temperature=st.session_state.temperature)
            )
            st.session_state["sns_result"] = result
        except RuntimeError as e:
            st.error(str(e))

if st.session_state.get("sns_result"):
    st.download_button(
        "テキストでダウンロード",
        st.session_state["sns_result"],
        file_name="sns_posts.txt",
    )
