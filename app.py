from flask import Flask, render_template, request
import random

app = Flask(__name__)

# ✅ Built-in syllabus (no files needed)
syllabus = {
    "physics": ["Motion", "Force", "Energy", "Waves", "Electricity"],
    "economics": ["Demand", "Supply", "Market", "Inflation", "GDP"],
    "biology": ["Cell", "Respiration", "Photosynthesis", "Genetics"],
    "math": ["Algebra", "Trigonometry", "Geometry", "Calculus"],
    "english": ["Grammar", "Comprehension", "Essay Writing"]
}

# 🧠 Quiz generator
def generate_quiz(subject):
    topic = random.choice(syllabus.get(subject, ["General Topic"]))
    return f"""
Topic: {topic}

What is {topic}?

A. Explanation of {topic}
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
        mode = request.form.get("mode")

        if mode == "quiz":
            result = generate_quiz(subject)
        else:
            topics = syllabus.get(subject, [])
            result = "Topics:\n" + "\n".join(topics)

    return render_template("index.html", result=result, subjects=subjects)


if __name__ == "__main__":
    app.run(debug=True)