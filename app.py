import os

from flask import Flask, request, render_template_string
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

PAGE = '''
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
            border-radius: 10px;
            white-space: pre-wrap;
        }

        .analysis {
            background: #f0f7ff;
        }

        .translation {
            background: #f5f5f5;
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

    {% if error %}

    <div class="box error">
        <h2>エラー</h2>
        {{ error }}
    </div>

    {% endif %}

</body>
</html>
'''


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

                # STEP 1：原文分析

                analysis_instructions = (
                    "You are the source-analysis engine for Borderless. "
                    "Analyze the Japanese source text before translation. "
                    "Return the analysis in Japanese using exactly these headings:\n"
                    "【カテゴリ】\n"
                    "【想定読者】\n"
                    "【トーン】\n"
                    "【文体】\n"
                    "【固有名詞・専門用語】\n"
                    "【翻訳時の注意点】\n"
                    "Focus on information that helps another AI translate "
                    "accurately for an international audience. "
                    "Do not translate the article. "
                    "Do not invent information not present in the source."
                )

                analysis_response = client.responses.create(
                    model="gpt-5.6-luna",
                    instructions=analysis_instructions,
                    input=original,
               
