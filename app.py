from flask import Flask, render_template, request, session, redirect
import random
import requests
import json
import os
import PyPDF2

app = Flask(__name__)
app.secret_key = "secret123"

HF_API_KEY = os.getenv("HF_API_KEY")

# ========================
# SYLLABUS
# ========================
syllabus = {
    "physics": {
        "Motion": "Motion is the change in position of an object over time.",
        "Force": "Force is a push or pull acting on an object.",
        "Energy": "Energy is the ability to do work."
    },
    "math": {
        "Algebra": "Algebra involves solving equations using variables.",
        "Trigonometry": "Trigonometry deals with angles and triangles.",
        "Geometry": "Geometry studies shapes and space."
    }
}

# ========================
# MEMORY
# ========================
def save_chat(chat):
    with open("chat.json", "w") as f:
        json.dump(chat, f)

def load_chat():
    try:
        with open("chat.json") as f:
            return json.load(f)
    except:
        return []

# ========================
# FILE READER
# ========================
def read_file(file):
    try:
        if file.filename.endswith(".txt"):
            return file.read().decode("utf-8")

        elif file.filename.endswith(".pdf"):
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text

        else:
            return "Unsupported file type."
    except:
        return "Error reading file."

# ========================
# WIKIPEDIA
# ========================
def search_wikipedia(query):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
    try:
        res = requests.get(url)
        data = res.json()
        return data.get("extract", "No info found.")
    except:
        return "Error fetching info."

# ========================
# AI
# ========================
def ask_ai(prompt):
    if not HF_API_KEY:
        return "⚠️ API key not set."

    url = "https://api-inference.huggingface.co/models/google/flan-t5-large"

    headers = {
        "Authorization": f"Bearer {HF_API_KEY}"
    }

    payload = {
        "inputs": prompt
    }

    try:
        res = requests.post(url, headers=headers, json=payload)
        data = res.json()

        if isinstance(data, list):
            return data[0].get("generated_text", "No response")

        return "⏳ AI loading, try again..."
    except:
        return "❌ AI error"

# ========================
# SMART TEACH
# ========================
def smart_teach(subject, question):
    topics = syllabus.get(subject, {})

    if question:
        question = question.lower()

        for topic, explanation in topics.items():
            if topic.lower() in question:
                return f"📘 {topic}\n\n{explanation}"

        wiki = search_wikipedia(question.replace(" ", "_"))
        if "No info" not in wiki:
            return f"🌐 {wiki}"

        ai = ask_ai(f"Explain simply: {question}")
        return f"🤖 {ai}"

    return "Ask something to learn."

# ========================
# QUIZ
# ========================
def generate_quiz(subject):
    topics = syllabus.get(subject, {})
    if not topics:
        return None

    topic = random.choice(list(topics.keys()))
    correct = topics[topic]

    options = [correct, "Wrong", "Incorrect", "Guess"]
    random.shuffle(options)

    return {"question": f"What is {topic}?", "options": options, "correct": correct}

# ========================
# MAIN
# ========================
@app.route("/", methods=["GET", "POST"])
def index():

    if "chat" not in session:
        session["chat"] = load_chat()

    if "name" not in session:
        session["name"] = None

    if "score" not in session:
        session["score"] = 0

    if "total" not in session:
        session["total"] = 0

    if request.method == "POST":

        # SET NAME
        if "set_name" in request.form:
            session["name"] = request.form.get("name")
            return redirect("/")

        # FILE UPLOAD
        if "file" in request.files:
            file = request.files["file"]

            if file.filename != "":
                content = read_file(file)
                content = content[:2000]

                ai = ask_ai(f"Explain this:\n{content}")

                session["chat"].append({
                    "role": "bot",
                    "text": f"📄 File Explanation:\n\n{ai}"
                })

                save_chat(session["chat"])
                return redirect("/")

        # QUIZ ANSWER
        if "answer" in request.form:
            user = request.form.get("answer")
            correct = session.get("correct")

            session["total"] += 1

            if user == correct:
                session["score"] += 1
                session["chat"].append({"role": "bot", "text": "✅ Correct!"})
            else:
                session["chat"].append({"role": "bot", "text": f"❌ Correct: {correct}"})

            save_chat(session["chat"])
            return redirect("/")

        # NORMAL INPUT
        subject = request.form.get("subject")
        question = request.form.get("question")
        mode = request.form.get("mode")

        session["chat"].append({"role": "user", "text": question or subject})

        if mode == "quiz":
            quiz = generate_quiz(subject)
            if quiz:
                session["correct"] = quiz["correct"]

                text = quiz["question"] + "\n\n"
                for i, opt in enumerate(quiz["options"]):
                    text += f"{i+1}. {opt}\n"

                session["chat"].append({"role": "bot", "text": text})
        else:
            response = smart_teach(subject, question)
            session["chat"].append({"role": "bot", "text": response})

        save_chat(session["chat"])

    return render_template(
        "index.html",
        chat=session["chat"],
        name=session["name"],
        score=session["score"],
        total=session["total"],
        subjects=list(syllabus.keys())
    )

if __name__ == "__main__":
    app.run(debug=True)