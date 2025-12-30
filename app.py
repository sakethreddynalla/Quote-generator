import requests
import mysql.connector
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session

load_dotenv()

# ---------- API CONFIG ----------
API_KEY = os.getenv("NINJA_API_KEY")
API_URL = "https://api.api-ninjas.com/v1/quotes"

if not API_KEY:
    raise ValueError("API key not found. Check your .env file.")

headers = {
    "X-Api-Key": API_KEY
}

# ---------- DATABASE CONFIG ----------
con = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_DATABASE")
)

# ---------- FLASK APP ----------
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")




def generate_ai_quote():
    try:
        response = requests.get(API_URL, headers=headers)
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            return data[0]["quote"], data[0]["author"]
    except Exception as e:
        print(e)
    return "No quote received", "Unknown"

# ---------- ROUTES ----------

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/ai")
def ai():
    quote, author = generate_ai_quote()
    return render_template("index.html", quote=quote, author=author)

@app.route("/registration", methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        user = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        cursor = con.cursor()
        cursor.execute(
            "INSERT INTO registration (username, email, password) VALUES (%s, %s, %s)",
            (user, email, password)
        )
        con.commit()
        cursor.close()

        return "Registration Successful"
    return render_template("registration.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        password = request.form["password"]

        cursor = con.cursor()
        cursor.execute(
            "SELECT * FROM registration WHERE username=%s AND password=%s",
            (user, password)
        )
        result = cursor.fetchone()
        cursor.close()

        if result:
            return redirect("/ai")
        else:
            return "Invalid Credentials"

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))


# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)