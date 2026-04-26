from flask import Flask, render_template, request, session, redirect
import random

app = Flask(__name__)
app.secret_key = "secret123"

# 📚 Expanded syllabus
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
    },
    "biology": {
        "Cell": "A cell is the basic unit of life.",
        "Photosynthesis": "Plants use sunlight to make food.",
        "Respiration": "Cells release energy from food."
    },
    "economics": {
        "Demand": "Demand is what consumers are willing to buy.",
        "Supply": "Supply is what producers are willing to sell.",
        "Market": "A place where buyers and sellers meet."
    },
    "english": {
        "Grammar": "Grammar is the structure of language.",
        "Essay": "An essay expresses ideas clearly.",
        "Comprehension": "Understanding written text."
    }
}

# 🧠 Smart teaching
def smart_teach(subject, question):
    topics = syllabus.get(subject, {})

    if not topics:
        return "No content available."

    if question:
        question = question.lower()

        for topic, explanation in topics.items():
            if topic.lower() in question:
                return f"📘 {topic}\n\n{explanation}\n\n💡 Example: This appears in exams and real life."

        return "🤔 I understand your question, but I need more data to explain better."

    # No question → explain all
    response = "📚 Key Topics:\n\n"
    for topic, explanation in topics.items():
        response += f"🔹 {topic}: {explanation}\n\n"

    return response


# 🧪 Quiz
def generate_quiz(subject):
    topics = syllabus.get(subject, {})
    if not topics:
        return None

    topic = random.choice(list(topics.keys()))
    correct = topics[topic]

    options = [
        correct,
        "Wrong definition",
        "Unrelated idea",
        "Incorrect explanation"
    ]

    random.shuffle(options)

    return {
        "question": f"What is {topic}?",
        "options": options,
        "correct": correct
    }


@app.route("/", methods=["GET", "POST"])
def index():
    subjects = list(syllabus.keys())

    # Init session
    if "chat" not in session:
        session["chat"] = []

    if "name" not in session:
        session["name"] = None

    if "score" not in session:
        session["score"] = 0

    if "questions" not in session:
        session["questions"] = 0

    if request.method == "POST":

        # Set name
        if "set_name" in request.form:
            session["name"] = request.form.get("name")
            return redirect("/")

        # Clear chat
        if "clear_chat" in request.form:
            session["chat"] = []
            return redirect("/")

        # Submit answer
        if "answer" in request.form:
            user_answer = request.form.get("answer")
            correct = session.get("correct_answer")

            session["questions"] += 1

            if user_answer == correct:
                session["score"] += 1
                session["chat"].append({"role": "bot", "text": "✅ Correct!"})
            else:
                session["chat"].append({"role": "bot", "text": f"❌ Wrong! Correct: {correct}"})

            return redirect("/")

        subject = request.form.get("subject")
        question = request.form.get("question")
        mode = request.form.get("mode")

        user_msg = question if question else subject
        session["chat"].append({"role": "user", "text": user_msg})

        if mode == "quiz":
            quiz = generate_quiz(subject)

            if quiz:
                session["correct_answer"] = quiz["correct"]

                text = quiz["question"] + "\n\n"
                for i, opt in enumerate(quiz["options"]):
                    text += f"{i+1}. {opt}\n"

                session["chat"].append({"role": "bot", "text": text})

        else:
            response = smart_teach(subject, question)
            session["chat"].append({"role": "bot", "text": response})

    return render_template(
        "index.html",
        chat=session["chat"],
        subjects=subjects,
        name=session["name"],
        score=session["score"],
        total=session["questions"]
    )


if __name__ == "__main__":
    app.run(debug=True)