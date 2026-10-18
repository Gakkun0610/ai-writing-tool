# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## これは何か

個人用（シングルユーザー・認証/DBなし）のAIライティング支援アプリ。StreamlitとGemini APIで構築されている。ブログ下書き、メール返信、要約、校正・リライト、翻訳、タイトル生成、SNS投稿文作成といった複数のライティングツールを、1つのマルチページStreamlitアプリにまとめている。

## コマンド

```powershell
# セットアップ (Windows / PowerShell)
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# APIキーの設定（どちらか一方でよい）
copy .env.example .env   # その後 .env を編集して GEMINI_API_KEY を設定
# — もしくは、アプリ起動後にサイドバーへ直接キーを入力（そのセッション内のみ有効）

# アプリの起動
streamlit run Home.py

# 全ファイルのコンパイルチェック（このリポジトリにテストスイートは無い）
python -m py_compile Home.py utils/*.py pages/*.py
```

テストスイート・リンター・ビルド手順はこのリポジトリには存在しない。変更を確認する際は、実際にアプリを起動しブラウザで該当ページを操作すること。

## アーキテクチャ

**Streamlitのマルチページアプリ** — `Home.py`がエントリーポイント。`pages/`配下の各ファイル（`1_..7_`と番号付き）がそれぞれ独立したライティングツールで、Streamlitのファイルベースルーティングにより自動的にナビゲーションへ追加される。すべてのページファイルは同じ構造に従う。

1. `utils/ui.py`の`setup_page(title, icon)`を呼ぶ — ページ設定、共通サイドバーの描画、ページタイトルの設定を行う。
2. ツール固有の入力を集める`st.form(...)`。
3. 送信時、フォーム入力からプロンプト文字列を組み立て、`utils/gemini_client.py`の`stream_generate(...)`を呼び出し、その結果を`st.write_stream(...)`に渡す。
4. 生成結果を`st.session_state[...]`にキャッシュし、再生成せずにダウンロードボタンを下部に表示できるようにする。

**`utils/gemini_client.py`** がGemini APIとの唯一の連携ポイント（`google-genai` SDK、`from google import genai`を使用）。`get_api_key()`は以下の優先順位で認証情報を解決する：`st.secrets["GEMINI_API_KEY"]` → 環境変数`GEMINI_API_KEY`（`.env`を`python-dotenv`で読み込み） → `st.session_state["gemini_api_key"]`（サイドバーのテキスト入力）。`stream_generate()`はテキストチャンクをストリーミング表示用にyieldするジェネレータで、キーが未設定の場合は日本語のユーザー向けメッセージ付きで`RuntimeError`を送出し、各ページ側でこれをキャッチして`st.error`で表示する。

**`utils/ui.py`** は全ページ共通のサイドバーを一元管理する：APIキー入力欄（環境変数/secretsにキーが見つからない場合のみ表示）、モデル選択（`gemini_client.py`の`AVAILABLE_MODELS`）、temperatureスライダー。ここで設定されるセッションステートのキー（`model`、`temperature`、`gemini_api_key`）は、すべてのページから直接読み取られる。

**新しいツールを追加する場合**は、`pages/`配下に番号付きの新しいファイルを追加し、上記の4ステップと同じ構造に従えばよい。ツールごとにプロンプト構造がそれぞれ異なるため、共通のプロンプト構築の抽象化はあえて設けておらず、文字列連結のみで構成している。

## 開発環境に関する注意点

- **このディレクトリはまだgitリポジトリではない**（`.git`が存在しない）。コミットやブランチ操作を求められた場合は、先に`git init`が必要になる点に注意。
- 作業ディレクトリのパスに**スペースと日本語文字**を含む（`...\デスクトップ\cursor学習用\AI writing tool`）。Bashツール経由でコマンドを実行する場合は、パスを必ずダブルクォートで囲むこと。
- `.venv`（仮想環境）と`.env`（APIキー入りの実ファイル）はこのマシン上に既に作成済みで、どちらも`.gitignore`済み。再作成の指示がない限り、`python -m venv .venv`を再実行する必要はない。
- 動作確認済みの依存バージョン：Python 3.14.6 / streamlit 1.64.0 / google-genai 2.25.0 / python-dotenv 1.2.3。`requirements.txt`は下限指定（`>=`）のみなので、将来的にこれより新しいバージョンが入る可能性がある。
- Streamlitはポートが使用中だと起動に失敗する（`Port 8501 is not available`）。動作確認のためにアプリを起動する際は、既存プロセスが残っていないか確認するか、`--server.port`で別ポートを指定すること。

## UIの言語と規約

- ユーザー向けの文字列（ラベル、ボタン、エラーメッセージ、Geminiに送るプロンプト）はすべて日本語。新しいページを追加する際もこれに合わせること。
- ページのファイル名は`<順番>_<絵文字>_<日本語ラベル>.py`という形式。Streamlitはファイル名からサイドバーのナビゲーションラベルを生成するため、ファイル名中の絵文字・ラベルは単なる見た目ではなくユーザーに直接表示される。
- データベース・認証・サーバー側の永続化は無し。リラン(rerun)をまたいで保持したい情報は`st.session_state`に置く。ブラウザセッションを超えて残るものは想定していない。
