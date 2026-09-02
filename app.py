from flask import Flask, render_template, request, redirect, url_for, flash, g
import pyodbc

app = Flask(__name__)
app.secret_key = "jopus5005135"  # needed for flash messages

# --- SQL Connection configuration ---
SERVER_NAME = r".\SQLEXPRESS"
DATABASE_NAME = "StudentDB"

CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={SERVER_NAME};"
    f"DATABASE={DATABASE_NAME};"
    "Trusted_Connection=yes;"
)


def get_db():
   
    # Opens one connection per request, reused across the request if called
    # more than once, and stashed on Flask's request-scoped 'g' object.
    
    if "db" not in g:
        g.db = pyodbc.connect(CONNECTION_STRING)
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    # Runs automatically after every request, even if it errored.
    db = g.pop("db", None)
    if db is not None:
        db.close()


# --- Routes ---
# home
@app.route("/")
def home():
    return render_template("index.html")

# add
@app.route("/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip()
        name = request.form.get("name", "").strip()
        course = request.form.get("course", "").strip()

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO Students (StudentID, Name, Course) VALUES (?, ?, ?)",
                student_id, name, course
            )
            conn.commit()
            flash(f"Student '{name}' was added.", "success")
            return redirect(url_for("add_student"))
        except pyodbc.IntegrityError:
            flash(f"A student with ID '{student_id}' already exists.", "error")
        except pyodbc.Error as e:
            flash(f"Database error: {e}", "error")

    return render_template("add.html")

# view
@app.route("/view")
def view_students():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT StudentID, Name, Course FROM Students ORDER BY StudentID")
    students = cursor.fetchall()
    return render_template("view.html", students=students)

# delete
@app.route("/delete", methods=["GET", "POST"])
def delete_student():
    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip()

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Students WHERE StudentID = ?", student_id)
            if cursor.rowcount == 0:
                flash(f"No student found with ID '{student_id}'.", "error")
            else:
                conn.commit()
                flash(f"Student '{student_id}' was deleted.", "success")
        except pyodbc.Error as e:
            flash(f"Database error: {e}", "error")

        return redirect(url_for("delete_student"))

    return render_template("delete.html")

@app.route("/update", methods=["GET", "POST"])
def update_student():
    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip()
        new_name = request.form.get("name", "").strip
        new_course = request.form.get("course", "").strip()

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE Students SET Name = ?, Course = ?, WHERE StudentID = ?",
                new_name, new_course, student_id
            )
        except pyodbc.Error as e:
            flash(f"Databse error: {e}", "error")

        return redirect(url_for("update_student"))
    
    student_id = request.args.get("student_id", "").strip()
    student = None

    if student_id:
        conn = get_db()
        cursor = conn.cursor
        cursor.execute(
            "SELECT StudentID, Name, Course FROM Students WHERE StudentID = ?", student_id
        )
        student = cursor.fetchone()
        if not student:
            flash(f"No student found with iD '{student_id}'.", "error")

    return render_template("update.html", student=student, searched_id=student_id)


if __name__ == "__main__":
    app.run(debug=True)