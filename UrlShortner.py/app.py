from flask import Flask, render_template, request, redirect
import sqlite3
import random
import string
import qrcode
import os

app = Flask(__name__)

DATABASE = "database.db"


# -------------------------
# Database Initialization
# -------------------------
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT NOT NULL,
            short_code TEXT UNIQUE NOT NULL,
            clicks INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# -------------------------
# Generate Random Short Code
# -------------------------
def generate_short_code(length=6):
    characters = string.ascii_lowercase + string.digits

    while True:
        code = ''.join(random.choice(characters) for _ in range(length))

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM urls WHERE short_code=?",
            (code,)
        )

        exists = cursor.fetchone()
        conn.close()

        if not exists:
            return code


# -------------------------
# Home Page
# -------------------------
@app.route("/")
def home():
    return render_template("index.html")
# -------------------------
# History Page
# -------------------------
@app.route("/history")
def history():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id,
               original_url,
               short_code,
               clicks,
               created_at
        FROM urls
        ORDER BY id DESC
    """)

    urls = cursor.fetchall()

    conn.close()

    return render_template(
        "history.html",
        urls=urls
    )


# -------------------------
# Generate Short URL
# -------------------------
@app.route("/shorten", methods=["POST"])
def shorten():

    original_url = request.form["url"].strip()
    custom_alias = request.form.get("custom_alias", "").strip().lower()

    # Add https:// automatically
    if not original_url.startswith(("http://", "https://")):
        original_url = "https://" + original_url

    # Use custom alias if provided
    if custom_alias:
        short_code = custom_alias
    else:
        short_code = generate_short_code()

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Check duplicate alias
    cursor.execute(
        "SELECT id FROM urls WHERE short_code=?",
        (short_code,)
    )

    if cursor.fetchone():
        conn.close()
        return """
        <h2 style='color:red;text-align:center;margin-top:40px;'>
        This custom alias already exists.<br><br>
        <a href="/">Go Back</a>
        </h2>
        """

    # Save URL
    cursor.execute(
        """
        INSERT INTO urls(original_url, short_code)
        VALUES(?,?)
        """,
        (original_url, short_code)
    )

    conn.commit()
    conn.close()

    short_url = request.host_url + short_code
# Generate QR Code
    qr = qrcode.make(short_url)

    qr_folder = os.path.join("static", "qr")

    if not os.path.exists(qr_folder):
        os.makedirs(qr_folder)

    qr_filename = short_code + ".png"

    qr_path = os.path.join(qr_folder, qr_filename)

    qr.save(qr_path)

    return render_template(
        "result.html",
        short_url=short_url,
        original_url=original_url,
        qr_image=qr_filename
    )


# -------------------------
# Redirect Short URL
# -------------------------
@app.route("/<short_code>")
def redirect_url(short_code):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT original_url
        FROM urls
        WHERE short_code=?
        """,
        (short_code,)
    )

    result = cursor.fetchone()
    print("short_code:", short_code)
    print("Database result:", result)

    if result:

        cursor.execute(
            """
            UPDATE urls
            SET clicks = clicks + 1
            WHERE short_code=?
            """,
            (short_code,)
        )

        conn.commit()
        conn.close()

        return redirect(result[0])

    conn.close()

    return render_template("404.html"), 404
# -------------------------
# Delete URL
# -------------------------
@app.route("/delete/<int:url_id>")
def delete_url(url_id):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM urls WHERE id=?",
        (url_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/history")


# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)