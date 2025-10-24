# 体育振り返りアプリ 🏃‍♂️

小学3年生を対象とした体育の振り返り支援アプリです。児童が選択肢を選びながら振り返りを記入し、Gemini AIが温かいフィードバックを生成します。

## 機能

- **単元選択**: 幅跳び、跳び箱、ゴール型ゲーム、ネット型ゲームから選択
- **3つの振り返り項目**:
  - 今日の課題
  - できたこと
  - 次の時間の課題
- **選択肢による入力支援**: テキスト入力のハードルを下げる
- **AI フィードバック**: Gemini APIによる個別のコメント生成
- **自由記述欄**: さらに詳しく書きたい児童向け
- **データ保存**: 振り返り内容をJSON形式で保存

## セットアップ

### 1. 必要なパッケージのインストール

```bash
# 仮想環境の作成（推奨）
python -m venv venv
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate  # Windows

# パッケージのインストール
pip install -r requirements.txt
```

### 2. Gemini API キーの取得

1. [Google AI Studio](https://makersuite.google.com/app/apikey) にアクセス
2. APIキーを生成
3. `.env.example` をコピーして `.env` を作成
4. `.env` ファイルに取得したAPIキーを設定

```bash
cp .env.example .env
# .envファイルを編集してAPIキーを設定
```

`.env` の内容:
```
GEMINI_API_KEY=あなたのAPIキー
```

### 3. アプリケーションの起動

```bash
python app.py
```

ブラウザで `http://localhost:5000` にアクセスしてください。

## 使い方

1. **単元を選択**: 4つの単元から今日の授業内容を選ぶ
2. **課題を選択**: 各セクションで当てはまる項目にチェック
3. **自由記述（任意）**: 追加で書きたいことがあれば入力
4. **送信**: 「振り返りを送る」ボタンをクリック
5. **AIコメント**: 先生からの励ましのコメントが表示される

## ファイル構成

```
PE_Reflection/
├── app.py                  # Flaskアプリケーション本体
├── requirements.txt        # Python依存パッケージ
├── .env                    # 環境変数（APIキー）
├── .gitignore             # Git除外設定
├── README.md              # このファイル
├── templates/
│   └── index.html         # HTMLテンプレート
├── static/
│   └── style.css          # CSSスタイル
└── data/                  # 振り返りデータ保存フォルダ（自動生成）
    └── reflection_*.json  # 保存された振り返り
```

## 技術スタック

- **バックエンド**: Python, Flask
- **フロントエンド**: HTML, CSS, JavaScript
- **AI**: Google Gemini API
- **データ保存**: JSON形式

## カスタマイズ

### 選択肢の変更

`app.py` の `UNIT_DATA` 辞書を編集することで、各単元の選択肢をカスタマイズできます。

```python
UNIT_DATA = {
    "幅跳び": {
        "今日の課題": [...],
        "できたこと": [...],
        "次の課題": [...]
    },
    ...
}
```

### AIプロンプトの調整

`app.py` の `generate_reflection()` 関数内のプロンプトを編集することで、AIの応答スタイルを変更できます。

## 注意事項

- Gemini APIの使用には Google アカウントが必要です
- APIの使用量には制限があります（無料枠あり）
- 本番環境で使用する場合は、適切なセキュリティ対策を実施してください

## ライセンス

このプロジェクトは教育目的で作成されています。

## 作成者

2025年
