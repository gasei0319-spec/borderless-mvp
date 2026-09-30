from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return """
    <!doctype html>
    <html lang="ja">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Borderless</title>
    </head>
    <body>
        <h1>Borderless</h1>
        <p>ワンクリックで世界へ。</p>
        <p>MVP is running.</p>
    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
