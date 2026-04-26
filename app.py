from flask import Flask, render_template, request
import os

app = Flask(__name__)

def load_subject(subject):
    path = f"syllabus/{subject}.txt"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "No content found."

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""

    if request.method == "POST":
        subject = request.form["subject"]
        question = request.form["question"]

        syllabus = load_subject(subject)

        result = f"""
Subject: {subject}

Topic: {question}

From syllabus:
{syllabus[:1000]}
"""

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)