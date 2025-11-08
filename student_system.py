# student_system.py
import sqlite3

DB_FILE = "student.db"

def create_connection():
    """Return a sqlite3 connection (creates file if not exists)."""
    return sqlite3.connect(DB_FILE)

def initialize_db():
    """Create the students table if it doesn't exist."""
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        roll_no INTEGER UNIQUE NOT NULL,
        course TEXT,
        marks INTEGER
    );
    """)
    conn.commit()
    conn.close()

def add_student(name, roll_no, course, marks):
    """Insert one student record into the database."""
    conn = create_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO students (name, roll_no, course, marks) VALUES (?, ?, ?, ?)",
            (name, roll_no, course, marks)
        )
        conn.commit()
        print("✅ Student added successfully!")
    except sqlite3.IntegrityError:
        print("❌ Roll number already exists! Use a unique roll number.")
    except Exception as e:
        print("❌ Error adding student:", e)
    finally:
        conn.close()

def view_students():
    """Fetch and print all students sorted by roll number."""
    conn = create_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name, roll_no, course, marks FROM students ORDER BY roll_no;")
        rows = cur.fetchall()
        if not rows:
            print("No students found.")
            return
        print("\n--- All Students ---")
        for r in rows:
            print(f"ID: {r[0]} | Name: {r[1]} | Roll: {r[2]} | Course: {r[3]} | Marks: {r[4]}")
        print("--------------------\n")
    except Exception as e:
        print("❌ Error reading students:", e)
    finally:
        conn.close()

def find_student_by_roll(roll_no):
    """Return a single student tuple by roll number or None."""
    conn = create_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name, roll_no, course, marks FROM students WHERE roll_no = ?;", (roll_no,))
        row = cur.fetchone()
        return row
    except Exception as e:
        print("❌ Error searching by roll:", e)
        return None
    finally:
        conn.close()

def search_students_by_name(name_part):
    """Return list of student tuples where name contains name_part (case-sensitive)."""
    conn = create_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name, roll_no, course, marks FROM students WHERE name LIKE ? ORDER BY roll_no;", (f"%{name_part}%",))
        rows = cur.fetchall()
        return rows
    except Exception as e:
        print("❌ Error searching by name:", e)
        return []
    finally:
        conn.close()

def update_student(roll_no, new_course=None, new_marks=None):
    """Update course and/or marks for a student with given roll number."""
    if new_course is None and new_marks is None:
        print("Nothing to update.")
        return
    conn = create_connection()
    cur = conn.cursor()
    try:
        if new_course is not None and new_marks is not None:
            cur.execute("UPDATE students SET course = ?, marks = ? WHERE roll_no = ?", (new_course, new_marks, roll_no))
        elif new_course is not None:
            cur.execute("UPDATE students SET course = ? WHERE roll_no = ?", (new_course, roll_no))
        elif new_marks is not None:
            cur.execute("UPDATE students SET marks = ? WHERE roll_no = ?", (new_marks, roll_no))
        conn.commit()
        if cur.rowcount == 0:
            print("❌ No student found with that roll number.")
        else:
            print("✅ Student updated successfully.")
    except Exception as e:
        print("❌ Error updating student:", e)
    finally:
        conn.close()

def delete_student(roll_no):
    """Delete a student by roll number after confirmation."""
    conn = create_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM students WHERE roll_no = ?", (roll_no,))
        conn.commit()
        if cur.rowcount == 0:
            print("❌ No student found with that roll number.")
        else:
            print("🗑️ Student deleted.")
    except Exception as e:
        print("❌ Error deleting student:", e)
    finally:
        conn.close()

def safe_int_input(prompt, min_val=None, max_val=None):
    """Prompt until a valid integer is entered (optional bounds)."""
    while True:
        v = input(prompt).strip()
        try:
            n = int(v)
            if min_val is not None and n < min_val:
                print(f"Enter a value >= {min_val}")
                continue
            if max_val is not None and n > max_val:
                print(f"Enter a value <= {max_val}")
                continue
            return n
        except ValueError:
            print("Please enter a valid integer.")

def main_menu():
    initialize_db()
    while True:
        print("\n--- Student Management System ---")
        print("1. Add Student")
        print("2. View All Students")
        print("3. Search Student by Roll")
        print("4. Search Students by Name")
        print("5. Update Student")
        print("6. Delete Student")
        print("7. Exit")

        choice = input("Choose (1-7): ").strip()

        if choice == '1':
            name = input("Enter name: ").strip()
            roll_no = safe_int_input("Enter roll number: ", min_val=1)
            course = input("Enter course: ").strip()
            marks = safe_int_input("Enter marks (0-100): ", min_val=0, max_val=100)
            add_student(name, roll_no, course, marks)

        elif choice == '2':
            view_students()

        elif choice == '3':
            roll = safe_int_input("Enter roll number to search: ", min_val=1)
            s = find_student_by_roll(roll)
            if s:
                print(f"Found -> ID:{s[0]} | Name:{s[1]} | Roll:{s[2]} | Course:{s[3]} | Marks:{s[4]}")
            else:
                print("No student found with that roll number.")

        elif choice == '4':
            q = input("Enter full or partial name to search: ").strip()
            results = search_students_by_name(q)
            if not results:
                print("No matching students found.")
            else:
                print(f"\n--- Search results for '{q}' ---")
                for r in results:
                    print(f"ID:{r[0]} | Name:{r[1]} | Roll:{r[2]} | Course:{r[3]} | Marks:{r[4]}")
                print("-------------------------------\n")

        elif choice == '5':
            roll = safe_int_input("Enter roll number to update: ", min_val=1)
            existing = find_student_by_roll(roll)
            if not existing:
                print("No student found with that roll number.")
            else:
                print(f"Current -> Name:{existing[1]} | Roll:{existing[2]} | Course:{existing[3]} | Marks:{existing[4]}")
                new_course = input("New course (leave blank to keep): ").strip()
                new_course = new_course if new_course != "" else None
                marks_input = input("New marks (0-100) (leave blank to keep): ").strip()
                new_marks = int(marks_input) if marks_input != "" else None
                if new_marks is not None and (new_marks < 0 or new_marks > 100):
                    print("Marks must be between 0 and 100.")
                else:
                    update_student(roll, new_course, new_marks)

        elif choice == '6':
            roll = safe_int_input("Enter roll number to delete: ", min_val=1)
            existing = find_student_by_roll(roll)
            if not existing:
                print("No student found with that roll number.")
            else:
                print(f"About to delete -> Name:{existing[1]} | Roll:{existing[2]}")
                confirm = input("Type 'yes' to confirm delete: ").strip().lower()
                if confirm == 'yes':
                    delete_student(roll)
                else:
                    print("Delete aborted.")

        elif choice == '7':
            print("Goodbye 👋")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main_menu()
