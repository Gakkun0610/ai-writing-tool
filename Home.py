import streamlit as st

from utils.gemini_client import is_ready
from utils.ui import setup_page

setup_page("AI Writing Tool", "🖋️")

st.write("個人用のAIライティング支援ツールです。左のメニューから使いたい機能を選んでください。")

if not is_ready():
    st.info(
        "はじめに、左のサイドバーで Gemini APIキーを入力するか、"
        "`.env` に `GEMINI_API_KEY` を設定してください。",
        icon="🔑",
    )

st.subheader("使える機能")

tools = [
    ("pages/1_📝_ブログ記事作成.py", "📝", "ブログ記事作成", "テーマとキーワードから記事の下書きを生成します。"),
    ("pages/2_📧_メール返信作成.py", "📧", "メール返信作成", "受信メールと返信方針から返信文を作成します。"),
    ("pages/3_📄_文章要約.py", "📄", "文章要約", "長文を指定した形式・長さで要約します。"),
    ("pages/4_✍️_校正リライト.py", "✍️", "校正・リライト", "誤字脱字チェックやトーンの変換を行います。"),
    ("pages/5_🌐_翻訳.py", "🌐", "翻訳", "指定した言語・トーンに翻訳します。"),
    ("pages/6_💡_タイトル生成.py", "💡", "タイトル・見出し生成", "記事内容から複数のタイトル案を生成します。"),
    ("pages/7_📱_SNS投稿文作成.py", "📱", "SNS投稿文作成", "X / Instagram などプラットフォーム別の投稿文を作成します。"),
]

cols = st.columns(2)
for i, (path, icon, label, desc) in enumerate(tools):
    with cols[i % 2]:
        with st.container(border=True):
            st.markdown(f"#### {icon} {label}")
            st.caption(desc)
            st.page_link(path, label=f"{label}を開く", icon="➡️")
