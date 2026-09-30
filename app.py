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
        body {
            font-family: system-ui, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 50px 20px;
            line-height: 1.7;
        }

        textarea {
            width: 100%;
            min-height: 200px;
            box-sizing: border-box;
            padding: 15px;
            font-size: 16px;
        }

        button {
            margin-top: 15px;
            padding: 13px 25px;
            font-size: 16px;
            cursor: pointer;
        }

        .box {
            margin-top: 30px;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 10px;
            white-space: pre-wrap;
        }

        .analysis {
            background: #f0f7ff;
        }

        .error {
            background: #fff0f0;
        }
    </style>
</head>

<body>

    <h1>Borderless</h1>

    <p>ワンクリックで世界へ。</p>

    <form method="POST">

        <textarea
            name="text"
            placeholder="海外へ届けたい日本語を入力"
            required>{{ original }}</textarea>

        <br>

        <button type="submit">
            世界へ届ける
        </button>

    </form>


    {% if analysis %}

    <div class="box analysis">

        <h2>記事分析</h2>

        {{ analysis }}

    </div>

    {% endif %}


    {% if translation %}

    <div class="box">

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

                # -------------------------
                # STEP 1
                # 日本語原文を分析
                # -------------------------

                analysis_response = client.responses.create(

                    model="gpt-5.6-luna",

                    instructions="""
You are the source-analysis engine for Borderless.

Analyze the Japanese source text before translation.

Return the analysis in Japanese using exactly these headings:

【カテゴリ】
【想定読者】
【トーン】
【文体】
【固有名詞・専門用語】
【翻訳時の注意点】

Focus especially on information that will help another AI
translate the article accurately for an international audience.

Do not translate the article.
Do not invent information that is not present in the source.
""",

                    input=original,
                )

                analysis = analysis_response.output_text


                # -------------------------
                # STEP 2
                # 分析結果を使って翻訳
                # -------------------------

                translation_input = f"""
以下の日本語原文を英語へ翻訳してください。

--- SOURCE ANALYSIS ---

{analysis}

--- JAPANESE SOURCE ---

{original}
"""


                translation_response = client.responses.create(

                    model="gpt-5.6-luna",

                    instructions="""
You are the translation engine for Borderless.

Translate the Japanese source into natural English
for an international audience.

Use the supplied source analysis as translation guidance.

Requirements:

- Preserve the original meaning and facts.
- Preserve the author's tone and personality.
- Preserve names, numbers, dates, URLs and product names.
- Avoid
