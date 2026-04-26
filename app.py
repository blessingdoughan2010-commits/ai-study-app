from flask import Flask, render_template, request, session, redirect
import random

app = Flask(__name__)
app.secret_key = "secret123"

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

def smart_teach(subject, question):
    topics = syllabus.get(subject, {})
    if not topics:
        return "No content available."

    if question:
        question = question.lower()
        for topic, explanation in topics.items():
            if topic.lower() in question:
                return f"📘 {topic}\n\n{explanation}\n\n💡 Example: Used in real life."
        return "🤔 I need more info to answer better."

    response = "📚 Topics:\n\n"
    for topic, explanation in topics.items():
        response += f"🔹 {topic}: {explanation}\n\n"
    return response


def generate_quiz(subject):
    topics = syllabus.get(subject, {})
    if not topics:
        return None

    topic = random.choice(list(topics.keys()))
    correct = topics[topic]

    options = [correct, "Wrong answer", "Incorrect idea", "Random guess"]
    random.shuffle(options)

    return {"question": f"What is {topic}?", "options": options, "correct": correct}


@app.route("/", methods=["GET", "POST"])
def index():
    if "chat" not in session:
        session["chat"] = []
    if "name" not in session:
        session["name"] = None
    if "score" not in session:
        session["score"] = 0
    if "total" not in session:
        session["total"] = 0

    if request.method == "POST":

        if "set_name" in request.form:
            session["name"] = request.form.get("name")
            return redirect("/")

        if "answer" in request.form:
            user = request.form.get("answer")
            correct = session.get("correct")

            session["total"] += 1

            if user == correct:
                session["score"] += 1
                session["chat"].append({"role": "bot", "text": "✅ Correct!"})
            else:
                session["chat"].append({"role": "bot", "text": f"❌ Wrong! Correct: {correct}"})

            return redirect("/")

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

    return render_template("index.html",
                           chat=session["chat"],
                           name=session["name"],
                           score=session["score"],
                           total=session["total"],
                           subjects=list(syllabus.keys()))


if __name__ == "__main__":
    app.run(debug=True)