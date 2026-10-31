import sqlite3
from functools import wraps
from flask import (
    Flask, request, redirect, url_for,
    session, flash, render_template_string
)
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.secret_key = "change-this-secret-key"
DATABASE = "course_registration.db"
MAX_CREDITS = 20
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_code TEXT UNIQUE NOT NULL,
            course_name TEXT NOT NULL,
            credits INTEGER NOT NULL,
            study_day TEXT NOT NULL,
            start_slot INTEGER NOT NULL,
            end_slot INTEGER NOT NULL,
            capacity INTEGER NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            course_id INTEGER NOT NULL,
            UNIQUE(student_id, course_id),
            FOREIGN KEY(student_id) REFERENCES students(student_id),
            FOREIGN KEY(course_id) REFERENCES courses(id)
        )
    """)
    student = conn.execute(
        "SELECT * FROM students WHERE student_id = ?",
        ("SV001",)
    ).fetchone()
    if not student:
        conn.execute("""
            INSERT INTO students VALUES (?, ?, ?)
        """, (
            "SV001",
            "Nguyen Van A",
            generate_password_hash("123456")
        ))
    sample_courses = [
        ("CS101", "Python Programming", 3, "Monday", 1, 3, 40),
        ("CS102", "Database Systems", 3, "Tuesday", 4, 6, 40),
        ("CS103", "Software Engineering", 3, "Monday", 2, 4, 35),
        ("CS104", "Computer Networks", 3, "Wednesday", 1, 3, 30),
        ("CS105", "Web Development", 4, "Thursday", 4, 6, 40)
    ]
    conn.executemany("""
        INSERT OR IGNORE INTO courses
        (course_code, course_name, credits, study_day,
         start_slot, end_slot, capacity)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, sample_courses)
    conn.commit()
    conn.close()
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "student_id" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper
LOGIN_PAGE = """
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Student Login</title>
<style>
body {
    font-family: Arial;
    background: #edf2f7;
    display: flex;
    justify-content: center;
    padding-top: 100px;
}
.box {
    background: white;
    padding: 30px;
    width: 350px;
    border-radius: 12px;
    text-align: center;
}
input, button {
    width: 100%;
    padding: 12px;
    margin: 8px 0;
    box-sizing: border-box;
}
button {
    background: #1769aa;
    color: white;
    border: none;
    cursor: pointer;
}
</style>
</head>
<body>
<div class="box">
    <h2>COURSE REGISTRATION</h2>
    <h3>Student Login</h3>
    {% for message in get_flashed_messages() %}
        <p style="color:red">{{ message }}</p>
    {% endfor %}
    <form method="POST">
        <input name="student_id"
               placeholder="Student ID" required>
        <input name="password" type="password"
               placeholder="Password" required>
        <button type="submit">Login</button>
    </form>
    <p>Demo: SV001 / 123456</p>
</div>
</body>
</html>
"""
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        student_id = request.form["student_id"].strip()
        password = request.form["password"]
        conn = get_db()
        student = conn.execute("""
            SELECT * FROM students WHERE student_id = ?
        """, (student_id,)).fetchone()
        conn.close()
        if student and check_password_hash(
            student["password"], password
        ):
            session.clear()
            session["student_id"] = student["student_id"]
            session["full_name"] = student["full_name"]
            return redirect(url_for("home"))
        flash("Invalid student ID or password!")
    return render_template_string(LOGIN_PAGE)
HOME_PAGE = """
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Course Registration</title>
<style>
body {
    font-family: Arial;
    background: #f1f4f9;
    padding: 25px;
}
.container {
    background: white;
    padding: 25px;
    max-width: 1100px;
    margin: auto;
    border-radius: 12px;
}
h2 { color: #1769aa; text-align: center; }
table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0 30px;
}
th, td {
    border: 1px solid #ddd;
    padding: 12px;
    text-align: center;
}
th { background: #1769aa; color: white; }
button {
    background: #1769aa;
    color: white;
    padding: 8px 14px;
    border: none;
    cursor: pointer;
}
.cancel { background: #d62828; }
.message { color: #d62828; font-weight: bold; }
</style>
</head>
<body>
<div class="container">
<h2>COURSE REGISTRATION SYSTEM</h2>
<p>Welcome, <b>{{ name }}</b> ({{ student_id }})</p>
<a href="{{ url_for('logout') }}">Logout</a>
{% for message in get_flashed_messages() %}
    <p class="message">{{ message }}</p>
{% endfor %}
<h3>Available Courses</h3>
<form method="GET">
    <input name="search" placeholder="Search course..."
           value="{{ keyword }}">
    <button type="submit">Search</button>
</form>
<table>
<tr>
    <th>Code</th>
    <th>Course Name</th>
    <th>Credits</th>
    <th>Day</th>
    <th>Time</th>
    <th>Capacity</th>
    <th>Action</th>
</tr>
{% for course in courses %}
<tr>
    <td>{{ course.course_code }}</td>
    <td>{{ course.course_name }}</td>
    <td>{{ course.credits }}</td>
    <td>{{ course.study_day }}</td>
    <td>{{ course.start_slot }}-{{ course.end_slot }}</td>
    <td>{{ course.enrolled }}/{{ course.capacity }}</td>
    <td>
        <form method="POST"
              action="{{ url_for('register', course_id=course.id) }}">
            <button type="submit">Register</button>
        </form>
    </td>
</tr>
{% endfor %}
</table>
<h3>Registered Courses</h3>
<p>Total Credits: <b>{{ total_credits }}/20</b></p>
<table>
<tr>
    <th>Code</th>
    <th>Course Name</th>
    <th>Credits</th>
    <th>Action</th>
</tr>
{% for course in registered %}
<tr>
    <td>{{ course.course_code }}</td>
    <td>{{ course.course_name }}</td>
    <td>{{ course.credits }}</td>
    <td>
        <form method="POST"
              action="{{ url_for('cancel', course_id=course.id) }}">
            <button class="cancel" type="submit">Cancel</button>
        </form>
    </td>
</tr>
{% endfor %}
</table>
</div>
</body>
</html>
"""
@app.route("/home")
@login_required
def home():
    keyword = request.args.get("search", "").strip()
    student_id = session["student_id"]
    conn = get_db()
    courses = conn.execute("""
        SELECT c.*,
        (SELECT COUNT(*) FROM registrations r
         WHERE r.course_id = c.id) AS enrolled
        FROM courses c
        WHERE c.course_code LIKE ? OR c.course_name LIKE ?
    """, (f"%{keyword}%", f"%{keyword}%")).fetchall()
    registered = conn.execute("""
        SELECT c.*
        FROM courses c
        JOIN registrations r ON c.id = r.course_id
        WHERE r.student_id = ?
    """, (student_id,)).fetchall()
    total_credits = sum(c["credits"] for c in registered)
    conn.close()
    return render_template_string(
        HOME_PAGE,
        courses=courses,
        registered=registered,
        total_credits=total_credits,
        student_id=student_id,
        name=session["full_name"],
        keyword=keyword
    )
@app.route("/register/<int:course_id>", methods=["POST"])
@login_required
def register(course_id):
    conn = get_db()
    student_id = session["student_id"]
    try:
        conn.execute("BEGIN IMMEDIATE")
        course = conn.execute("""
            SELECT * FROM courses WHERE id = ?
        """, (course_id,)).fetchone()
        if not course:
            flash("Course not found!")
            conn.rollback()
            return redirect(url_for("home"))
        current = conn.execute("""
            SELECT c.*
            FROM courses c
            JOIN registrations r ON c.id = r.course_id
            WHERE r.student_id = ?
        """, (student_id,)).fetchall()
        if any(c["id"] == course_id for c in current):
            flash("You have already registered this course!")
        elif sum(c["credits"] for c in current) + course["credits"] > MAX_CREDITS:
            flash("Maximum credit limit is 20!")
        elif any(
            c["study_day"] == course["study_day"]
            and c["start_slot"] <= course["end_slot"]
            and course["start_slot"] <= c["end_slot"]
            for c in current
        ):
            flash("Schedule conflict detected!")
        else:
            count = conn.execute("""
                SELECT COUNT(*) FROM registrations
                WHERE course_id = ?
            """, (course_id,)).fetchone()[0]
            if count >= course["capacity"]:
                flash("Course is full!")
            else:
                conn.execute("""
                    INSERT INTO registrations (student_id, course_id)
                    VALUES (?, ?)
                """, (student_id, course_id))
                flash("Registration successful!")
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        flash("Registration failed. Please try again.")
    finally:
        conn.close()
    return redirect(url_for("home"))
@app.route("/cancel/<int:course_id>", methods=["POST"])
@login_required
def cancel(course_id):
    conn = get_db()
    conn.execute("""
        DELETE FROM registrations
        WHERE student_id = ? AND course_id = ?
    """, (session["student_id"], course_id))
    conn.commit()
    conn.close()

    flash("Course cancelled successfully!")
    return redirect(url_for("home"))
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
if __name__ == "__main__":
    init_db()
    app.run(debug=True)

