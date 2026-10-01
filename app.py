import os

from flask import Flask, request, render_template_string
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

PAGE = """
<!doctype html>
<html lang="ja">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Borderless</title>
    <style>
        body { font-family: system-ui, sans-serif; max-width: 800px; margin: 0 auto; padding: 40px 20px; line-height: 1.7; }
        textarea { width: 100%; min-height: 200px; box-sizing: border-box; padding: 15px; font-size: 16px; }
        button { margin-top: 15px; padding: 13px 25px; font-size: 16px; cursor: pointer; }
        .box { margin-top: 30px; padding: 20px; border-radius: 10px; white-space: pre-wrap; }
        .analysis { background: #f0f7ff; }
        .translation { background: #f5f5f5; }
        .error { background: #fff0f0; }
    </style>
</head>
<body>
    <h1>Borderless</h1>
    <p>ワンクリックで世界へ。</p>

    <form method="POST">
        <textarea name="text" placeholder="海外へ届けたい日本語を入力" required>{{ original }}</textarea>
        <br>
        <button type="submit">世界へ届ける</button>
    </form>

    {% if analysis %}
    <div class="box analysis">
        <h2>記事分析</h2>
        {{ analysis }}
    </div>
    {% endif %}

    {% if translation %}
    <div class="box translation">
        <h2>English</h2>
        {{ translation }}
    </div>
    {% endif %}

    {% if error %}
    <div class="box error">
        <h2>エラー</h2>
        {{ error }}
    </div>
    {% endif %}
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def home():
    original = ""
    analysis = ""
    translation = ""
    error = ""

    if request.method == "POST":
        original = request.form.get("text", "").strip()

        if not original:
            error = "文章を入力してください。"
        else:
            try:
                analysis_instructions = (
                    "You are the source-analysis engine for Borderless. "
                    "Analyze the Japanese source text before translation. "
                    "Return the analysis in Japanese with these headings: "
                    "【カテゴリ】 【想定読者】 【トーン】 【文体】 "
                    "【固有名詞・専門用語】 【翻訳時の注意点】. "
                    "Focus only on information useful for accurate translation. "
                    "Do not translate the article and do not invent information."
                )

                analysis_response = client.responses.create(
                    model="gpt-5.6-luna",
                    instructions=analysis_instructions,
                    input=original,
                )
                analysis = analysis_response.output_text

                translation_instructions = (
                    "You are the translation engine for Borderless. "
                    "Translate the Japanese source into natural English for an international audience. "
                    "Use the supplied source analysis as guidance. "
                    "Preserve meaning, facts, tone, names, numbers, dates, URLs and product names. "
                    "Avoid unnatural literal phrasing. "
                    "Clarify Japanese cultural context only when necessary. "
                    "Never invent unsupported information. "
                    "Do not summarize or unnecessarily shorten the source. "
                    "Output only the final English translation."
                )

                translation_input = (
                    "SOURCE ANALYSIS:\n"
                    + analysis
                    + "\n\nJAPANESE SOURCE:\n"
                    + original
                )

                translation_response = client.responses.create(
                    model="gpt-5.6-luna",
                    instructions=translation_instructions,
                    input=translation_input,
                )
                translation = translation_response.output_text

            except Exception as exc:
                print(f"OpenAI error: {exc}", flush=True)
                error = "AI処理中にエラーが発生しました。しばらくしてからもう一度試してください。"

    return render_template_string(
        PAGE,
        original=original,
        analysis=analysis,
        translation=translation,
        error=error,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
