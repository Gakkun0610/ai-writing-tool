import streamlit as st

from utils.gemini_client import stream_generate
from utils.ui import MAX_CHARS_LONG, MAX_CHARS_SHORT, setup_page

setup_page("メール返信作成", "📧")

st.caption("受信メールの内容と返信の方針を入力すると、返信文の下書きを作成します。")

with st.form("email_form"):
    original_email = st.text_area("受信したメール本文*", max_chars=MAX_CHARS_LONG, height=200, placeholder="相手からのメールをそのまま貼り付けてください")
    intent = st.text_area(
        "返信で伝えたいこと*",
        max_chars=MAX_CHARS_LONG,
        height=100,
        placeholder="例：日程は来週水曜14時でOK。資料は金曜までに送ると伝えたい。",
    )
    tone = st.selectbox("トーン", ["ビジネス・丁寧", "フォーマル・かしこまった", "親しみやすい", "簡潔・要点のみ"])
    relationship = st.text_input("相手との関係（任意）", max_chars=MAX_CHARS_SHORT, placeholder="例：初めて取引する取引先の担当者")

    submitted = st.form_submit_button("返信文を生成", type="primary", use_container_width=True)

if submitted:
    if not original_email.strip() or not intent.strip():
        st.error("受信メール本文と、伝えたい内容の両方を入力してください。")
    else:
        prompt_parts = [
            "あなたは日本のビジネスマナーに詳しいアシスタントです。以下の受信メールに対する返信メールを作成してください。",
            f"# 受信メール\n{original_email}",
            f"# 返信で伝えたいこと\n{intent}",
            f"# トーン\n{tone}",
        ]
        if relationship.strip():
            prompt_parts.append(f"# 相手との関係\n{relationship}")
        prompt_parts.append(
            "宛名・書き出しの挨拶・本文・結びの挨拶・署名欄（〇〇の部分はプレースホルダーでよい）を含む、"
            "そのまま送れる形式のメール文面を作成してください。件名も提案してください。"
        )
        prompt = "\n\n".join(prompt_parts)

        st.subheader("生成結果")
        try:
            result = st.write_stream(
                stream_generate(prompt, model=st.session_state.model, temperature=st.session_state.temperature)
            )
            st.session_state["email_result"] = result
        except RuntimeError as e:
            st.error(str(e))

if st.session_state.get("email_result"):
    st.download_button(
        "テキストでダウンロード",
        st.session_state["email_result"],
        file_name="email_reply.txt",
    )
