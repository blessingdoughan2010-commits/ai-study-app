from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import requests, os, json, random, PyPDF2

app = Flask(__name__)
app.secret_key = "secret123"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
db = SQLAlchemy(app)

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

# ================= AI =================
def ask_ai(prompt):
    url = "https://api-inference.huggingface.co/models/google/flan-t5-large"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    try:
        res = requests.post(url, headers=headers, json={"inputs": prompt})
        data = res.json()
        if isinstance(data, list):
            return data[0].get("generated_text", "No response")
    except:
        return "AI error"

# ================= FILE =================
def read_file(file):
    if file.filename.endswith(".txt"):
        return file.read().decode("utf-8")
    if file.filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        text = ""
        for p in reader.pages:
            text += p.extract_text() or ""
        return text
    return "Unsupported file"

# ================= ROUTES =================

@app.route("/", methods=["GET","POST"])
@login_required
def index():

    chat = json.loads(current_user.chat)

    if request.method == "POST":

        # FILE
        if "file" in request.files:
            f = request.files["file"]
            if f.filename:
                content = read_file(f)[:2000]
                reply = ask_ai(f"Explain:\n{content}")
                chat.append({"role":"bot","text":reply})

        # QUIZ ANSWER
        elif "answer" in request.form:
            ans = request.form.get("answer")
            correct = session.get("correct")
            current_user.total += 1

            if ans == correct:
                current_user.score += 1
                chat.append({"role":"bot","text":"✅ Correct"})
            else:
                chat.append({"role":"bot","text":f"❌ Correct: {correct}"})

        else:
            q = request.form.get("question")
            chat.append({"role":"user","text":q})
            reply = ask_ai(q)
            chat.append({"role":"bot","text":reply})

        current_user.chat = json.dumps(chat)
        db.session.commit()

    return render_template("index.html",
                           chat=chat,
                           name=current_user.username,
                           score=current_user.score,
                           total=current_user.total)

# ================= LOGIN =================
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form.get("username")
        p = request.form.get("password")

        user = User.query.filter_by(username=u, password=p).first()
        if user:
            login_user(user)
            return redirect("/")
    return render_template("login.html")

# ================= REGISTER =================
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        u = request.form.get("username")
        p = request.form.get("password")

        user = User(username=u, password=p)
        db.session.add(user)
        db.session.commit()
        return redirect("/login")

    return render_template("register.html")

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    logout_user()
    return redirect("/login")

# ================= RUN =================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)