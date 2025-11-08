# gui.py
"""
Simple Tkinter GUI for the Student Management System.
Uses the same SQLite DB file (student.db) created by student_system.py.
Features: Add, View (list), Search by roll/name, Update, Delete.
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

DB_FILE = "student.db"

# ----------------- DB helpers (small, repeated logic) -----------------
def get_conn():
    return sqlite3.connect(DB_FILE)

def ensure_db():
    conn = get_conn()
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

def add_student_db(name, roll_no, course, marks):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO students (name, roll_no, course, marks) VALUES (?, ?, ?, ?)",
                    (name, roll_no, course, marks))
        conn.commit()
        return True, "Student added."
    except sqlite3.IntegrityError:
        return False, "Roll number already exists."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def fetch_all():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, roll_no, course, marks FROM students ORDER BY roll_no")
    rows = cur.fetchall()
    conn.close()
    return rows

def find_by_roll(roll):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, roll_no, course, marks FROM students WHERE roll_no = ?", (roll,))
    row = cur.fetchone()
    conn.close()
    return row

def search_by_name(part):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, roll_no, course, marks FROM students WHERE name LIKE ? ORDER BY roll_no", (f"%{part}%",))
    rows = cur.fetchall()
    conn.close()
    return rows

def update_student_db(roll_no, new_course=None, new_marks=None):
    conn = get_conn()
    cur = conn.cursor()
    if new_course is not None and new_marks is not None:
        cur.execute("UPDATE students SET course = ?, marks = ? WHERE roll_no = ?", (new_course, new_marks, roll_no))
    elif new_course is not None:
        cur.execute("UPDATE students SET course = ? WHERE roll_no = ?", (new_course, roll_no))
    elif new_marks is not None:
        cur.execute("UPDATE students SET marks = ? WHERE roll_no = ?", (new_marks, roll_no))
    conn.commit()
    rc = cur.rowcount
    conn.close()
    return rc > 0

def delete_student_db(roll_no):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE roll_no = ?", (roll_no,))
    conn.commit()
    rc = cur.rowcount
    conn.close()
    return rc > 0

# ----------------- GUI -----------------
class StudentGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        ensure_db()
        self.title("Student Management (GUI)")
        self.geometry("760x460")
        self.resizable(False, False)

        # Left frame: form
        frm_left = ttk.Frame(self, padding=12)
        frm_left.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(frm_left, text="Add / Update Student", font=("Segoe UI", 12, "bold")).pack(pady=(0,8))

        self.name_var = tk.StringVar()
        self.roll_var = tk.StringVar()
        self.course_var = tk.StringVar()
        self.marks_var = tk.StringVar()

        ttk.Label(frm_left, text="Name").pack(anchor=tk.W)
        ttk.Entry(frm_left, textvariable=self.name_var, width=30).pack()

        ttk.Label(frm_left, text="Roll No").pack(anchor=tk.W, pady=(6,0))
        ttk.Entry(frm_left, textvariable=self.roll_var, width=30).pack()

        ttk.Label(frm_left, text="Course").pack(anchor=tk.W, pady=(6,0))
        ttk.Entry(frm_left, textvariable=self.course_var, width=30).pack()

        ttk.Label(frm_left, text="Marks (0-100)").pack(anchor=tk.W, pady=(6,0))
        ttk.Entry(frm_left, textvariable=self.marks_var, width=30).pack()

        ttk.Button(frm_left, text="Add Student", command=self.on_add).pack(pady=(10,4), fill=tk.X)
        ttk.Button(frm_left, text="Update Student", command=self.on_update).pack(pady=4, fill=tk.X)
        ttk.Button(frm_left, text="Delete Student", command=self.on_delete).pack(pady=4, fill=tk.X)

        # Right frame: list + search
        frm_right = ttk.Frame(self, padding=12)
        frm_right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        top_search = ttk.Frame(frm_right)
        top_search.pack(fill=tk.X)

        ttk.Label(top_search, text="Search:").pack(side=tk.LEFT, padx=(0,6))
        self.search_var = tk.StringVar()
        ttk.Entry(top_search, textvariable=self.search_var, width=30).pack(side=tk.LEFT)
        ttk.Button(top_search, text="By Name", command=self.on_search_name).pack(side=tk.LEFT, padx=6)
        ttk.Button(top_search, text="By Roll", command=self.on_search_roll).pack(side=tk.LEFT)

        ttk.Button(top_search, text="Refresh All", command=self.refresh_list).pack(side=tk.RIGHT)

        # Treeview for listing students
        cols = ("ID", "Name", "Roll", "Course", "Marks")
        self.tree = ttk.Treeview(frm_right, columns=cols, show="headings", height=18)
        for c in cols:
            self.tree.heading(c, text=c)
            # set width
        self.tree.column("ID", width=40, anchor=tk.CENTER)
        self.tree.column("Name", width=220)
        self.tree.column("Roll", width=80, anchor=tk.CENTER)
        self.tree.column("Course", width=160)
        self.tree.column("Marks", width=80, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=(10,0))

        # Bind click to populate left form
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # initial load
        self.refresh_list()

    # ----------------- GUI actions -----------------
    def on_add(self):
        name = self.name_var.get().strip()
        roll = self.roll_var.get().strip()
        course = self.course_var.get().strip()
        marks = self.marks_var.get().strip()
        if not name or not roll:
            messagebox.showwarning("Input error", "Name and Roll are required.")
            return
        try:
            roll_i = int(roll)
            marks_i = int(marks) if marks != "" else None
            if marks_i is not None and (marks_i < 0 or marks_i > 100):
                messagebox.showwarning("Input error", "Marks must be 0-100.")
                return
        except ValueError:
            messagebox.showwarning("Input error", "Roll and Marks must be integers.")
            return
        ok, msg = add_student_db(name, roll_i, course, marks_i if marks != "" else None)
        if ok:
            messagebox.showinfo("Success", msg)
            self.clear_form()
            self.refresh_list()
        else:
            messagebox.showerror("Error", msg)

    def on_update(self):
        roll = self.roll_var.get().strip()
        if not roll:
            messagebox.showwarning("Input error", "Enter roll to update.")
            return
        try:
            roll_i = int(roll)
        except ValueError:
            messagebox.showwarning("Input error", "Roll must be integer.")
            return
        new_course = self.course_var.get().strip() or None
        marks_text = self.marks_var.get().strip()
        new_marks = int(marks_text) if marks_text != "" else None
        if new_marks is not None and (new_marks < 0 or new_marks > 100):
            messagebox.showwarning("Input error", "Marks must be 0-100.")
            return
        ok = update_student_db(roll_i, new_course, new_marks)
        if ok:
            messagebox.showinfo("Success", "Student updated.")
            self.clear_form()
            self.refresh_list()
        else:
            messagebox.showerror("Error", "No student with that roll number.")

    def on_delete(self):
        roll = self.roll_var.get().strip()
        if not roll:
            messagebox.showwarning("Input error", "Enter roll to delete.")
            return
        try:
            roll_i = int(roll)
        except ValueError:
            messagebox.showwarning("Input error", "Roll must be integer.")
            return
        confirm = messagebox.askyesno("Confirm delete", f"Delete student with roll {roll_i}?")
        if not confirm:
            return
        ok = delete_student_db(roll_i)
        if ok:
            messagebox.showinfo("Deleted", "Student deleted.")
            self.clear_form()
            self.refresh_list()
        else:
            messagebox.showerror("Error", "No student with that roll number.")

    def on_search_name(self):
        q = self.search_var.get().strip()
        if not q:
            messagebox.showwarning("Input", "Enter name or part of name to search.")
            return
        rows = search_by_name(q)
        self.populate_tree(rows)

    def on_search_roll(self):
        q = self.search_var.get().strip()
        if not q:
            messagebox.showwarning("Input", "Enter roll number to search.")
            return
        try:
            r = int(q)
        except ValueError:
            messagebox.showwarning("Input", "Roll must be an integer.")
            return
        row = find_by_roll(r)
        self.populate_tree([row] if row else [])

    def refresh_list(self):
        rows = fetch_all()
        self.populate_tree(rows)

    def populate_tree(self, rows):
        # clear
        for it in self.tree.get_children():
            self.tree.delete(it)
        for r in rows:
            if r is None:
                continue
            self.tree.insert("", tk.END, values=(r[0], r[1], r[2], r[3], r[4]))

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        # populate form
        self.name_var.set(vals[1])
        self.roll_var.set(vals[2])
        self.course_var.set(vals[3] or "")
        self.marks_var.set(vals[4] if vals[4] is not None else "")

    def clear_form(self):
        self.name_var.set("")
        self.roll_var.set("")
        self.course_var.set("")
        self.marks_var.set("")

if __name__ == "__main__":
    app = StudentGUI()
    app.mainloop()
