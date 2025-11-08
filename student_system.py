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
        print("5. Exit")

        choice = input("Choose (1-5): ").strip()

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
            print("Goodbye 👋")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main_menu()
