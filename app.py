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
            max-width: 760px;
            margin: 0 auto;
            padding: 50px 20px;
        }
        textarea {
            width: 100%;
            min-height: 180px;
            box-sizing: border-box;
            padding: 15px;
        }
        button {
            margin-top: 15px;
            padding: 12px 24px;
            font-size: 16px;
        }
        .result {
            margin-top: 30px;
            padding: 20px;
            background: #f5f5f5;
            white-space: pre-wrap;
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
        <button type="submit">世界へ届ける</button>
    </form>

    {% if translation %}
    <div class="result">
        <h2>English</h2>
        {{ translation }}
    </div>
    {% endif %}
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def home():
    original = ""
    translation = ""

    if request.method == "POST":
        original = request.form["text"]

        response = client.responses.create(
            model="gpt-5.6-luna",
            instructions=(
                "Translate the Japanese text into natural English for an "
                "international audience. Preserve the original meaning, facts, "
                "tone, names, numbers, and URLs. Do not add information that "
                "is not present in the source."
            ),
            input=original,
        )

        translation = response.output_text

    return render_template_string(
        PAGE,
        original=original,
        translation=translation,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
