from flask import Flask, render_template, request
import random

app = Flask(__name__)

# Built-in syllabus with explanations
syllabus = {
    "physics": {
        "Motion": "Motion is the change in position of an object over time. It can be described using speed, velocity, and acceleration.",
        "Force": "Force is a push or pull acting on an object. It can cause motion or change the shape of an object.",
        "Energy": "Energy is the ability to do work. Examples include kinetic and potential energy."
    },
    "math": {
        "Algebra": "Algebra involves solving equations and working with variables like x and y.",
        "Trigonometry": "Trigonometry studies relationships between angles and sides of triangles.",
        "Geometry": "Geometry deals with shapes, sizes, and properties of space.",
        "Calculus": "Calculus studies change and motion using derivatives and integrals."
    },
    "economics": {
        "Demand": "Demand is the quantity of goods consumers are willing to buy at a given price.",
        "Supply": "Supply is the quantity producers are willing to sell.",
        "Market": "A market is where buyers and sellers interact.",
    }
}

# 🧠 Teaching function
def teach(subject, question):
    topics = syllabus.get(subject, {})

    if not topics:
        return "No content available."

    # If user typed something → try match
    if question:
        for topic, explanation in topics.items():
            if question.lower() in topic.lower():
                return f"{topic}:\n{explanation}"

        return "I couldn't find that topic. Try another keyword."

    # If no question → explain a random topic
    topic = random.choice(list(topics.keys()))
    return f"{topic}:\n{topics[topic]}"


# 🧪 Quiz generator
def generate_quiz(subject):
    topics = list(syllabus.get(subject, {}).keys())

    if not topics:
        return "No quiz available."

    topic = random.choice(topics)

    return f"""
Topic: {topic}

What is {topic}?

A. Correct explanation of {topic}
B. Wrong answer
C. Another option
D. Random guess

Answer: A
"""


@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    subjects = list(syllabus.keys())

    if request.method == "POST":
        subject = request.form.get("subject")
        question = request.form.get("question")
        mode = request.form.get("mode")

        if mode == "quiz":
            result = generate_quiz(subject)
        else:
            result = teach(subject, question)

    return render_template("index.html", result=result, subjects=subjects)


if __name__ == "__main__":
    app.run(debug=True)