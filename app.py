import os

from flask import Flask, request, render_template_string
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

MODEL = "gpt-5.6-luna"

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
            padding: 40px 20px;
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
            border-radius: 10px;
            white-space: pre-wrap;
        }

        .analysis {
            background: #f0f7ff;
        }

        .translation {
            background: #f5f5f5;
        }

        .audit {
            background: #f2fff5;
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

    <div class="box translation">
        <h2>English</h2>
        {{ translation }}
    </div>

    {% endif %}


    {% if audit %}

    <div class="box audit">
        <h2>翻訳チェック</h2>
        {{ audit }}
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
    audit = ""
    error = ""

    if request.method == "POST":

        original = request.form.get("text", "").strip()

        if not original:

            error = "文章を入力してください。"

        else:

            try:

                # STEP 1：原文分析

                analysis_instructions = (
                    "You are the source-analysis engine for Borderless. "
                    "Analyze the Japanese source before translation. "
                    "Return the analysis in Japanese using these headings: "
                    "【カテゴリ】 【想定読者】 【トーン】 【文体】 "
                    "【固有名詞・専門用語】 【翻訳時の注意点】. "
                    "Do not translate the source. "
                    "Do not invent information."
                )

                analysis_response = client.responses.create(
                    model=MODEL,
                    instructions=analysis_instructions,
                    input=original,
                )

                analysis = analysis_response.output_text


                # STEP 2：翻訳

                translation_instructions = (
                    "You are the translation engine for Borderless. "
                    "Translate the Japanese source into natural English "
                    "for an international audience. "
                    "Use the supplied analysis as guidance
