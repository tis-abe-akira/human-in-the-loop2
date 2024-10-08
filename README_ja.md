# LangGraph ヒューマンインザループ チャットアプリケーション

このプロジェクトは、LangGraphを使用したヒューマンインザループチャットアプリケーションを示すものです。FastAPIバックエンドとReactフロントエンドで実装されており、AI駆動の会話フローに人間の承認をどのように統合するかを紹介しています。

## エージェントがツール利用を提案し人間が承認する場合
![hil_with_approve.gif](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/130262/bdcd2dfb-8c77-1784-dce7-b4972e2b7a39.gif)

## エージェントがツールを利用しない場合（承認は不要）
![hil_without_approve.gif](https://qiita-image-store.s3.ap-northeast-1.amazonaws.com/0/130262/64906c50-6f0a-e262-fde7-410ae12ff291.gif)

## 特徴

- LangGraphとOpenAIのGPTモデルを使用したAI駆動の会話
- AIのアクションを承認するためのヒューマンインザループ機能
- チャットロジックとAPIエンドポイントを処理するFastAPIバックエンド
- ユーザー対話のためのReactフロントエンド
- リアルタイムの更新と承認リクエスト

## プロジェクト構造

プロジェクトは主に2つの部分に分かれています：

1. バックエンド（FastAPI + Poetry）
2. フロントエンド（React + Vite）

### バックエンド

バックエンドは以下を担当します：
- 会話フローの管理
- LangGraphとOpenAIとの統合
- フロントエンド用のAPIエンドポイントの提供

### フロントエンド

フロントエンドは以下を提供します：
- チャットアプリケーションのユーザーフレンドリーなインターフェース
- 会話のリアルタイム更新
- メッセージの送信とAIアクションの承認のためのボタン

## 前提条件

- Python 3.8以上
- Node.js 14以上
- npm 6以上
- Poetry
- OpenAI APIキー

## セットアップ

### バックエンドのセットアップ

1. バックエンドディレクトリに移動します：
   ```
   cd langchain-hitl-backend
   ```

2. Poetryを使用して依存関係をインストールします：
   ```
   poetry install
   ```

3. バックエンドディレクトリに`.env`ファイルを作成し、OpenAI APIキーを追加します：
   ```
   OPENAI_API_KEY=あなたのopenai_api_keyをここに
   ```

4. バックエンドサーバーを実行します：
   ```
   poetry run uvicorn main:app --reload
   ```

バックエンドは`http://localhost:8000`で利用可能になります。

### フロントエンドのセットアップ

1. フロントエンドディレクトリに移動します：
   ```
   cd langchain-hitl-frontend
   ```

2. 依存関係をインストールします：
   ```
   npm install
   ```

3. 開発サーバーを実行します：
   ```
   npm run dev
   ```

フロントエンドは`http://localhost:5173`で利用可能になります。

## 使用方法

1. Webブラウザを開き、`http://localhost:5173`にアクセスします。
2. 入力フィールドにメッセージを入力し、「送信」をクリックして会話を開始します。
3. AIが応答し、特定のアクションに対して承認を求める場合があります。
4. プロンプトが表示されたら、AIの提案するアクションを確認し、同意する場合は「承認」をクリックします。
5. 必要に応じて会話を続けます。

## 貢献

貢献は歓迎します！プルリクエストを自由に提出してください。

## ライセンス

このプロジェクトはMITライセンスの下でライセンスされています - 詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 謝辞

- LangGraphフレームワークを提供してくれた[LangChain](https://github.com/hwchase17/langchain)
- GPTモデルを提供してくれた[OpenAI](https://openai.com/)
- バックエンドフレームワークの[FastAPI](https://fastapi.tiangolo.com/)
- フロントエンドライブラリの[React](https://reactjs.org/)
