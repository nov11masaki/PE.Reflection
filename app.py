import os
import json
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai

# 環境変数を読み込む
load_dotenv()

app = Flask(__name__)

# Gemini APIの設定
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

# 各単元の選択肢データ
UNIT_DATA = {
    "幅跳び": {
        "今日の課題": [
            "助走のスピードを上げる",
            "踏み切りのタイミング",
            "空中での姿勢",
            "着地の仕方",
            "リズムよく走る"
        ],
        "できたこと": [
            "力強く踏み切れた",
            "助走のスピードが上がった",
            "遠くまで跳べた",
            "バランスよく着地できた",
            "リズムよく助走できた"
        ],
        "次の課題": [
            "もっと遠くに跳ぶ",
            "助走をもっと速くする",
            "踏み切りを強くする",
            "着地を安定させる",
            "フォームをきれいにする"
        ]
    },
    "跳び箱": {
        "今日の課題": [
            "助走のスピード",
            "踏み切りの力強さ",
            "手のつき方",
            "足の開き方",
            "着地の安定"
        ],
        "できたこと": [
            "勢いよく踏み切れた",
            "手をしっかりついた",
            "足を大きく開けた",
            "着地が決まった",
            "怖がらずに跳べた"
        ],
        "次の課題": [
            "もっと高い段を跳ぶ",
            "きれいなフォームで跳ぶ",
            "着地を安定させる",
            "助走を速くする",
            "連続して跳ぶ"
        ]
    },
    "ゴール型ゲーム": {
        "今日の課題": [
            "パスをもらう動き",
            "パスを出すタイミング",
            "シュートの精度",
            "守りの位置取り",
            "チームで協力する"
        ],
        "できたこと": [
            "パスがつながった",
            "シュートが決まった",
            "良い位置に動けた",
            "仲間と声をかけ合えた",
            "ボールをうばえた"
        ],
        "次の課題": [
            "もっとパスをつなぐ",
            "シュートのチャンスを増やす",
            "守りを強くする",
            "チームワークを高める",
            "作戦を考える"
        ]
    },
    "ネット型ゲーム": {
        "今日の課題": [
            "ボールをよく見る",
            "返すタイミング",
            "ボールを落とさない",
            "仲間との連携",
            "相手コートに返す"
        ],
        "できたこと": [
            "ラリーが続いた",
            "良いところに返せた",
            "仲間と協力できた",
            "サーブが入った",
            "最後まであきらめなかった"
        ],
        "次の課題": [
            "もっとラリーを続ける",
            "作戦を立てる",
            "ねらったところに返す",
            "チームで声をかけ合う",
            "相手の苦手なところをつく"
        ]
    }
}


@app.route('/')
def index():
    """メインページを表示"""
    return render_template('index.html', units=list(UNIT_DATA.keys()))


@app.route('/get_options', methods=['POST'])
def get_options():
    """選択された単元の選択肢を返す"""
    data = request.json
    unit = data.get('unit')
    
    if unit in UNIT_DATA:
        return jsonify(UNIT_DATA[unit])
    else:
        return jsonify({"error": "単元が見つかりません"}), 404


@app.route('/generate_reflection', methods=['POST'])
def generate_reflection():
    """Gemini APIを使用して振り返りのアドバイスを生成"""
    data = request.json
    unit = data.get('unit')
    today_challenge = data.get('today_challenge', [])
    achieved = data.get('achieved', [])
    next_challenge = data.get('next_challenge', [])
    free_text = data.get('free_text', '')
    
    # 単元別の具体的な場の提案を含めたプロンプトを作成
    unit_specific_advice = {
        "幅跳び": "砂場の近くで練習したり、跳ぶ前に足のバネを使う練習をしてみよう",
        "跳び箱": "低い段から始めて、手をつく場所に目印をつけると良いよ",
        "ゴール型ゲーム": "パスの練習場を作ったり、チームで作戦タイムを作ってみよう",
        "ネット型ゲーム": "ペアでラリーの練習をする場を作ったり、ボールをよく見る練習をしてみよう"
    }
    
    prompt = f"""
あなたは小学3年生の体育の先生です。児童の振り返りに対して、温かく受け止め、次の学習につながる具体的なコメントを書いてください。

【単元】{unit}
【今日の課題】
{', '.join(today_challenge) if today_challenge else 'なし'}

【できたこと】
{', '.join(achieved) if achieved else 'なし'}

【次の時間の課題】
{', '.join(next_challenge) if next_challenge else 'なし'}

【自由記述】
{free_text if free_text else 'なし'}

以下の構成でコメントを書いてください:
1. **受け止め（共感）**: まず、児童のがんばりや気持ちをしっかり受け止める（「〜ができたんだね！」「〜をがんばっていたね」など）
2. **具体的なほめ言葉**: できたことを具体的にほめる
3. **次への提案**: 次の学習に向けて、具体的な練習方法や場の設定を提案する（例: 「次は〜の場所で〜を練習してみよう」「〜と一緒に〜をしてみるといいよ」など）
4. **励まし**: 前向きな励ましの言葉で締めくくる

注意点:
- 小学3年生にわかりやすい言葉を使う
- 抽象的な助言ではなく、具体的な練習方法や場の提案を含める
- {unit}に適した具体的なアドバイスを入れる（参考: {unit_specific_advice.get(unit, '')}）
- 150～200文字程度でまとめる
- 「〜しましょう」ではなく「〜してみよう」「〜するといいよ」など親しみやすい表現を使う

コメント:
"""
    
    try:
        # Gemini APIを使用してコメント生成
        response = model.generate_content(prompt)
        comment = response.text
        
        return jsonify({
            "success": True,
            "comment": comment
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/save_reflection', methods=['POST'])
def save_reflection():
    """振り返りを保存（将来的にデータベースに保存する機能）"""
    data = request.json
    
    # ここでは単純にファイルに保存
    try:
        # データディレクトリがなければ作成
        os.makedirs('data', exist_ok=True)
        
        # 日時をファイル名に含める
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"data/reflection_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            "success": True,
            "message": "振り返りを保存しました"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
