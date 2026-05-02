from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import requests, os, json, PyPDF2

# For EXE
import webbrowser
import threading

app = Flask(__name__)
app.secret_key = "secret123"

# DATABASE
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# LOGIN
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

HF_API_KEY = os.getenv("HF_API_KEY")

# ================= USER MODEL =================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    chat = db.Column(db.Text, default="[]")
    score = db.Column(db.Integer, default=0)
    total = db.Column(db.Integer, default=0)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# CREATE DB
with app.app_context():
    db.create_all()

# ================= AI =================
def ask_ai(prompt):
    url = "https://api-inference.huggingface.co/models/google/flan-t5-large"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}

    try:
        res = requests.post(url, headers=headers, json={"inputs": prompt})
        data = res.json()

        if isinstance(data, list):
            return data[0].get("generated_text", "No response")

        return "⏳ AI loading..."
    except Exception as e:
        print("AI ERROR:", e)
        return "❌ AI error"

# ================= FILE =================
def read_file(file):
    try:
        if file.filename.endswith(".txt"):
            return file.read().decode("utf-8")

        if file.filename.endswith(".pdf"):
            reader = PyPDF2.PdfReader(file)
            text = ""

            for page in reader.pages:
                content = page.extract_text()
                if content:
                    text += content

            if text.strip() == "":
                return "⚠️ Could not read text from PDF."

            return text

        return "Unsupported file format"

    except Exception as e:
        print("PDF ERROR:", e)
        return "❌ Error reading file"

# ================= ROUTES =================

@app.route("/")
def home():
    return redirect("/dashboard")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template(
        "dashboard.html",
        name=current_user.username,
        score=current_user.score,
        total=current_user.total
    )

# ================= LEARN =================
@app.route("/learn", methods=["GET", "POST"])
@login_required
def learn():

    chat = json.loads(current_user.chat)

    if request.method == "POST":

        if "file" not in request.files:
            chat.append({
                "role": "bot",
                "text": "📄 Please upload a file."
            })

        else:
            f = request.files["file"]

            if f.filename == "":
                chat.append({
                    "role": "bot",
                    "text": "⚠️ No file selected."
                })

            else:
                content = read_file(f)

                if "❌" in content or "⚠️" in content:
                    chat.append({
                        "role": "bot",
                        "text": content
                    })
                else:
                    reply = ask_ai(
                        f"You are a teacher. Teach this simply:\n{content[:1500]}"
                    )

                    chat.append({"role": "bot", "text": reply})

        current_user.chat = json.dumps(chat)
        db.session.commit()

    return render_template("learn.html", chat=chat)

# ================= QUIZ =================
@app.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():

    quiz_data = None

    if request.method == "POST":

        if "generate" in request.form:
            q = ask_ai("Create one multiple choice question with 4 options and indicate the correct answer.")

            quiz_data = {
                "question": q,
                "options": ["Option A", "Option B", "Option C", "Option D"]
            }

        if "answer" in request.form:
            current_user.total += 1
            current_user.score += 1
            db.session.commit()

    return render_template("quiz.html", quiz=quiz_data)

# ================= PROFILE =================
@app.route("/profile")
@login_required
def profile():
    return render_template(
        "profile.html",
        name=current_user.username,
        score=current_user.score,
        total=current_user.total
    )

# ================= LOGIN =================
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form.get("username")
        p = request.form.get("password")

        user = User.query.filter_by(username=u, password=p).first()

        if user:
            login_user(user)
            return redirect("/dashboard")

    return render_template("login.html")

# ================= REGISTER =================
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        u = request.form.get("username")
        p = request.form.get("password")

        if User.query.filter_by(username=u).first():
            return "User already exists"

        user = User(username=u, password=p)
        db.session.add(user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")

# ================= LOGOUT =================
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

# ================= AUTO OPEN (LOCAL ONLY) =================
def open_browser():
    webbrowser.open("http://127.0.0.1:5000")

# RUN
if __name__ == "__main__":
    # Only open browser locally (not on Render)
    if os.environ.get("RENDER") is None:
        threading.Timer(1, open_browser).start()

    app.run(host="0.0.0.0", port=5000)