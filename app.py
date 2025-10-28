import os
import json
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI

# 環境変数を読み込む
load_dotenv()

app = Flask(__name__)

# OpenAI APIの設定
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

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


@app.route('/regenerate_options', methods=['POST'])
def regenerate_options():
    """当てはまる選択肢がない場合、AIで新しい選択肢を生成"""
    data = request.json
    unit = data.get('unit')
    category = data.get('category')  # "今日の課題", "できたこと", "次の課題"
    selected_items = data.get('selected_items', [])  # 既に選択されている項目
    
    print(f"[DEBUG] Unit: {unit}, Category: {category}")  # デバッグログ
    print(f"[DEBUG] Selected items: {selected_items}")  # デバッグログ
    
    # 既に選択されている項目を除外して、必要な新しい選択肢の数を計算
    num_new_options = max(5 - len(selected_items), 3)  # 最低3つの新しい選択肢を生成
    
    prompt = f"""
小学3年生の体育「{unit}」の授業で、{category}について、児童が選べる選択肢を{num_new_options}つ作成してください。

要件:
1. 小学3年生にわかりやすい表現
2. 具体的で選びやすい内容
3. {unit}に適した内容
4. 簡潔な表現（15文字以内）
5. リスト形式で{num_new_options}つ

{"以下の項目は既に選択されているため、これらとは異なる選択肢を作成してください:" if selected_items else ""}
{chr(10).join(f"- {item}" for item in selected_items) if selected_items else ""}

必ず以下の形式で出力してください:
1. 選択肢1
2. 選択肢2
3. 選択肢3
{"4. 選択肢4" if num_new_options >= 4 else ""}
{"5. 選択肢5" if num_new_options >= 5 else ""}

注意: 番号と選択肢のみを出力し、他の説明は不要です。
"""
    
    try:
        print(f"[DEBUG] Calling OpenAI API...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたは小学3年生向けの体育学習支援アシスタントです。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=200
        )
        response_text = response.choices[0].message.content
        print(f"[DEBUG] Response received: {response_text}")
        
        # 行ごとに分割して番号を削除
        lines = response_text.strip().split('\n')
        new_options = []
        
        import re
        for line in lines:
            # 数字とピリオド、スペースを削除
            cleaned = line.strip()
            if cleaned:
                # "1. " や "1) " などの番号パターンを削除
                cleaned = re.sub(r'^\d+[\.\)]\s*', '', cleaned)
                # 前後の引用符を削除
                cleaned = cleaned.strip('"\'')
                if cleaned and len(cleaned) > 0:
                    new_options.append(cleaned)
        
        print(f"[DEBUG] Generated new options: {new_options}")
        
        # 既に選択されている項目を先頭に追加
        final_options = selected_items + new_options
        
        # 重複を削除しつつ順序を保持
        seen = set()
        final_options = [x for x in final_options if not (x in seen or seen.add(x))]
        
        print(f"[DEBUG] Final options (with selected): {final_options}")
        
        # 最低3つの選択肢がある場合のみ成功（選択済み含む）
        if len(final_options) >= 3:
            return jsonify({
                "success": True,
                "options": final_options[:8]  # 最大8つまで表示
            })
        else:
            error_msg = f"選択肢の生成に失敗しました（{len(final_options)}個しか生成できませんでした）"
            print(f"[ERROR] {error_msg}")
            return jsonify({
                "success": False,
                "error": error_msg
            }), 500
    except Exception as e:
        print(f"[ERROR] Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


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

以下の構成で、完全に日本語のみでコメントを書いてください（英語は一切使わない）:

1. **受け止め（共感）**: 児童のがんばりや気持ちをしっかり受け止める
   - 「〜ができたんだね」「〜をがんばっていたね」「〜に挑戦していたんだね」など
   
2. **具体的なほめ言葉**: できたことを具体的にほめる
   - 「〜が上手にできていたよ」「〜がとても良かったよ」など
   
3. **次への提案**: 具体的な練習方法や場の設定を提案する
   - 「次は〜の場所で〜を練習してみよう」
   - 「〜と一緒に〜をしてみるといいよ」
   - 「〜のコツは〜だよ」など
   - {unit}に適した具体的なアドバイス（例: {unit_specific_advice.get(unit, '')}）
   
4. **励まし**: 前向きな励ましの言葉で締めくくる
   - 「きっとできるようになるよ」「次も楽しみだね」など

【重要な注意点】
- 小学3年生が理解できる簡単な日本語のみを使用
- 英語や英単語は絶対に使わない
- 抽象的な表現ではなく、具体的な行動や場面を示す
- 「〜しましょう」ではなく「〜してみよう」「〜するといいよ」など親しみやすい表現
- 150～200文字程度
- 箇条書きや番号は使わず、自然な文章で書く

【日本語表現の改善視点】
- 児童が自分で次にやることをイメージできる具体的な言葉を使う
- 「もっと」「さらに」などの漠然とした表現より、「〜を3回練習する」「〜の位置に立つ」など明確な指示
- 体の動かし方は「ぐっと」「すっと」「ぎゅっと」などの擬態語も効果的
- 場所や人との関係性を具体的に示す（「友達と」「壁の前で」「線の上で」など）

コメント:
"""
    
    try:
        # OpenAI APIを使用してコメント生成
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたは小学3年生の体育学習を支援する先生です。児童の振り返りに対して、温かく受け止めつつ、次の学習につながる具体的なアドバイスをしてください。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        comment = response.choices[0].message.content
        
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
    app.run(debug=True, host='0.0.0.0', port=5004)
