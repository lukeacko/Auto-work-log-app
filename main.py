import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import sqlite3
import csv
from datetime import datetime

class WorkLogApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Work Log App")
        self.root.geometry("900x600")

        # Input variables
        self.jobnum_input = tk.StringVar()
        self.vin_input = tk.StringVar()
        self.tech_input = tk.StringVar()
        self.date_var = tk.StringVar(value="Choose Date")  # Date button text

        # Build UI
        self.create_input_section()
        self.create_buttons()

        # Initialize database and load technicians
        self.initialize_database()

        # Browser window placeholder
        self.browser_window = None

    # --------------------------
    # UI: Input Section
    # --------------------------
    def create_input_section(self):
        inputs = tk.LabelFrame(self.root, text="Job Data")
        inputs.pack(padx=10, pady=10, fill="x")

        # Job Number
        tk.Label(inputs, text="Job Number:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Entry(inputs, textvariable=self.jobnum_input, width=20).grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # VIN
        tk.Label(inputs, text="VIN:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        tk.Entry(inputs, textvariable=self.vin_input, width=20).grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # Technician
        tk.Label(inputs, text="Technician:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.tech_dropdown = ttk.Combobox(
            inputs,
            textvariable=self.tech_input,
            state="readonly",
            width=18
        )
        self.tech_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.tech_dropdown.set("Select...")
        self.tech_dropdown.bind("<<ComboboxSelected>>",
            lambda e: self.add_new_technician_for_popup(self.tech_dropdown, self.tech_input))

        # Date picker button
        tk.Label(inputs, text="Date:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.dateButton = tk.Button(inputs, textvariable=self.date_var, command=self.date_entry, width=15)
        self.dateButton.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        # Job Description
        tk.Label(self.root, text="Job Description:").pack(anchor="w", padx=12)
        self.jobdesc_input = tk.Text(self.root, height=5)
        self.jobdesc_input.pack(padx=10, pady=5, fill="x")

    # --------------------------
    # Buttons
    # --------------------------
    def create_buttons(self):
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Save Entry", command=self.save).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="Reset", command=self.reset).grid(row=0, column=1, padx=10)
        tk.Button(btn_frame, text="View Logs", command=self.view_logs).grid(row=0, column=2, padx=10)

    # --------------------------
    # Database Initialization
    # --------------------------
    def initialize_database(self):
        try:
            conn = sqlite3.connect("worklogs.db")
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    jobnum TEXT,
                    vin TEXT,
                    technician TEXT,
                    description TEXT,
                    date TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS technicians (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE
                )
            """)
            # Add default technicians if empty
            cursor.execute("SELECT COUNT(*) FROM technicians")
            if cursor.fetchone()[0] == 0:
                for name in ["John", "Mike", "Sarah", "Alex"]:
                    cursor.execute("INSERT INTO technicians (name) VALUES (?)", (name,))
            conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        finally:
            conn.close()
        self.load_technicians()

    # --------------------------
    # Load technicians from DB
    # --------------------------
    def load_technicians(self):
        conn = sqlite3.connect("worklogs.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM technicians ORDER BY name")
        rows = cursor.fetchall()
        conn.close()
        self.tech_list = [row[0] for row in rows] + ["Add new…"]
        if hasattr(self, "tech_dropdown"):
            self.tech_dropdown["values"] = self.tech_list

    # --------------------------
    # Add new technician
    # --------------------------
    def add_new_technician_for_popup(self, combobox, var):
        if var.get() != "Add new…":
            return
        popup = tk.Toplevel(self.root)
        popup.title("Add Technician")
        popup.geometry("250x120")

        tk.Label(popup, text="Enter new technician name:").pack(pady=5)
        new_name_var = tk.StringVar()
        tk.Entry(popup, textvariable=new_name_var).pack(pady=5)

        def save_new_name():
            name = new_name_var.get().strip()
            if name and name not in self.tech_list:
                try:
                    conn = sqlite3.connect("worklogs.db")
                    cursor = conn.cursor()
                    cursor.execute("INSERT OR IGNORE INTO technicians (name) VALUES (?)", (name,))
                    conn.commit()
                    conn.close()
                except sqlite3.Error as e:
                    messagebox.showerror("DB Error", f"An error occurred: {e}")
                self.load_technicians()  # Refresh dropdowns
                var.set(name)
            popup.destroy()

        tk.Button(popup, text="Save", command=save_new_name).pack(pady=5)

    # --------------------------
    # Date picker
    # --------------------------
    def date_entry(self):
        top = tk.Toplevel(self.root)
        tk.Label(top, text="Choose a date").pack(padx=10, pady=10)
        cal = DateEntry(top, width=12, background="darkblue", foreground="white")
        cal.pack(padx=10, pady=10)

        def save_date():
            self.date_var.set(cal.get())
            top.destroy()

        tk.Button(top, text="Save", command=save_date).pack(pady=10)

    # --------------------------
    # Save entry
    # --------------------------
    def save(self):
        jobnum = self.jobnum_input.get().strip()
        vin = self.vin_input.get().strip()
        technician = self.tech_input.get()
        jobdesc = self.jobdesc_input.get("1.0", "end-1c").strip()
        date = self.dateButton["text"]

        # Required fields
        if not jobnum or not vin or not technician or not jobdesc or date == "Choose Date":
            messagebox.showerror("Error", "Please fill all fields and select a date.")
            return

        # Job number validation
        if not jobnum.isdigit() or len(jobnum) > 5:
            messagebox.showerror("Invalid Job Number", "Job number must be numeric and up to 5 digits.")
            return

        # VIN validation
        if len(vin) != 17 or not vin.isalnum():
            messagebox.showerror("Invalid VIN", "VIN must be exactly 17 alphanumeric characters.")
            return

        # Save to DB
        conn = sqlite3.connect("worklogs.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO logs (jobnum, vin, technician, description, date) VALUES (?, ?, ?, ?, ?)",
            (jobnum, vin, technician, jobdesc, date)
        )
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Job added successfully!")
        self.reset()
        self.load_logs() if self.browser_window else None


    # --------------------------
    # Import & Export CSV
    # --------------------------
    def export_to_csv(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save logs as CSV"
        )
        if not file_path:
            return

        rows = [self.tree.item(child)["values"] for child in self.tree.get_children()]

        if not rows:
            messagebox.showwarning("No Data", "There are no logs to export.")
            return

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(self.columns)
                writer.writerows(rows)
            messagebox.showinfo("Export Successful", f"{len(rows)} logs exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred:\n{e}")

    def import_from_csv(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")],
            title="Select CSV file to import"
        )
        if not file_path:
            return

        try:
            with open(file_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows_added = 0
                conn = sqlite3.connect("worklogs.db")
                cursor = conn.cursor()
                for row in reader:
                    keys = {k.lower().strip(): k for k in row.keys()}
                    if all(col in keys for col in ("jobnum", "vin", "technician", "description", "date")):
                        tech_name = row[keys["technician"]].strip()
                        cursor.execute("INSERT OR IGNORE INTO technicians (name) VALUES (?)", (tech_name,))
                        cursor.execute("""
                            INSERT INTO logs (jobnum, vin, technician, description, date)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            row[keys["jobnum"]],
                            row[keys["vin"]],
                            tech_name,
                            row[keys["description"]],
                            row[keys["date"]]
                        ))
                        rows_added += 1
                conn.commit()
                conn.close()
            self.load_technicians()
            self.load_logs()
            messagebox.showinfo("Import Complete", f"{rows_added} jobs imported successfully!")
        except Exception as e:
            messagebox.showerror("Import Error", f"An error occurred:\n{e}")

    # --------------------------
    # Reset form
    # --------------------------
    def reset(self):
        self.jobnum_input.set("")
        self.vin_input.set("")
        self.tech_input.set("Select...")
        self.jobdesc_input.delete("1.0", "end")
        self.date_var.set("Choose Date")

    # --------------------------
    # Treeview button activation
    # --------------------------
    def on_tree_select(self, event):
        selected = self.tree.selection()
        state = "normal" if selected else "disabled"
        self.edit_button.config(state=state)
        self.delete_button.config(state=state)

    # --------------------------
    # View logs
    # --------------------------
    def view_logs(self):
        if self.browser_window:
            self.browser_window.destroy()

        self.browser_window = tk.Toplevel(self.root)
        self.browser_window.title("Work Log Viewer")
        self.browser_window.geometry("1000x550")  # slightly taller for status bar

        # Search frame
        search_frame = tk.Frame(self.browser_window)
        search_frame.pack(padx=5, pady=5, fill="x")

        tk.Label(search_frame, text="Search Job #:").grid(row=0, column=0, padx=5, pady=2)
        self.search_jobnum = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_jobnum, width=15).grid(row=0, column=1, padx=5)

        tk.Label(search_frame, text="Search VIN:").grid(row=0, column=2, padx=5, pady=2)
        self.search_vin = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_vin, width=15).grid(row=0, column=3, padx=5)

        tk.Label(search_frame, text="Search Technician:").grid(row=0, column=4, padx=5, pady=2)
        self.search_tech = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_tech, width=15).grid(row=0, column=5, padx=5)

        tk.Button(search_frame, text="Search", command=self.load_logs).grid(row=0, column=6, padx=5)
        tk.Button(search_frame, text="Clear", command=self.clear_search).grid(row=0, column=7, padx=5)

        # Treeview
        self.columns = ("id", "jobnum", "vin", "technician", "description", "date")
        self.tree = ttk.Treeview(self.browser_window, columns=self.columns, show="headings")
        self.tree.pack(fill="both", expand=True)

        for col in self.columns:
            width = 300 if col == "description" else 120
            self.tree.heading(col, text=col.title(), command=lambda c=col: self.sort_tree(c, False))
            self.tree.column(col, width=width)

        # Buttons
        btn_frame = tk.Frame(self.browser_window)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Refresh", command=self.load_logs).grid(row=0, column=0, padx=5)
        self.edit_button = tk.Button(btn_frame, text="Edit Selected", command=self.edit_selected_job, state="disabled")
        self.edit_button.grid(row=0, column=1, padx=5)
        self.delete_button = tk.Button(btn_frame, text="Delete Selected", command=self.delete_selected_job, state="disabled")
        self.delete_button.grid(row=0, column=2, padx=5)
        self.export_button = tk.Button(btn_frame, text="Export to CSV", command=self.export_to_csv)
        self.export_button.grid(row=0, column=3, padx=5)
        self.import_button = tk.Button(btn_frame, text="Import CSV", command=self.import_from_csv)
        self.import_button.grid(row=0, column=4, padx=5)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Jobs loaded: 0")
        status_label = tk.Label(self.browser_window, textvariable=self.status_var, anchor="w")
        status_label.pack(fill="x", padx=5, pady=2)

        # Bind treeview selection and double-click
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Double-1>", lambda e: self.edit_selected_job())

        # Load logs
        self.load_logs()

    # --------------------------
    # Load logs
    # --------------------------
    def load_logs(self):
        if not hasattr(self, "tree"):
            return
        for row in self.tree.get_children():
            self.tree.delete(row)

        jobnum_filter = self.search_jobnum.get().strip() if hasattr(self, "search_jobnum") else ""
        vin_filter = self.search_vin.get().strip() if hasattr(self, "search_vin") else ""
        tech_filter = self.search_tech.get().strip() if hasattr(self, "search_tech") else ""

        conn = sqlite3.connect("worklogs.db")
        cursor = conn.cursor()

        query = "SELECT * FROM logs WHERE 1=1"
        params = []

        if jobnum_filter:
            query += " AND jobnum LIKE ?"
            params.append(f"%{jobnum_filter}%")
        if vin_filter:
            query += " AND vin LIKE ?"
            params.append(f"%{vin_filter}%")
        if tech_filter:
            query += " AND technician LIKE ?"
            params.append(f"%{tech_filter}%")

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            self.tree.insert("", "end", values=row)

        # Update status bar
        self.status_var.set(f"Jobs loaded: {len(rows)}")

    # --------------------------
    # Clear search
    # --------------------------
    def clear_search(self):
        self.search_jobnum.set("")
        self.search_vin.set("")
        self.search_tech.set("")
        self.load_logs()

    # --------------------------
    # Sort Treeview
    # --------------------------
    def sort_tree(self, col, reverse):
        data = [(self.tree.item(child)["values"][self.columns.index(col)], child)
                for child in self.tree.get_children()]
        try:
            data.sort(key=lambda x: float(x[0]), reverse=reverse)
        except:
            data.sort(key=lambda x: str(x[0]).lower(), reverse=reverse)
        for idx, item in enumerate(data):
            self.tree.move(item[1], "", idx)
        self.tree.heading(col, command=lambda: self.sort_tree(col, not reverse))

    # --------------------------
    # Delete job
    # --------------------------
    def delete_selected_job(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a job to delete.")
            return
        item = self.tree.item(selected[0])
        job_id, jobnum = item["values"][0], item["values"][1]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Job #{jobnum}?"):
            conn = sqlite3.connect("worklogs.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM logs WHERE id=?", (job_id,))
            conn.commit()
            conn.close()
            self.tree.delete(selected[0])
            messagebox.showinfo("Deleted", f"Job #{jobnum} has been deleted.")

    # --------------------------
    # Edit job
    # --------------------------
    def edit_selected_job(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a job to edit.")
            return
        item = self.tree.item(selected[0])
        job_id, jobnum, vin, technician, description, date_str = item["values"]

        popup = tk.Toplevel(self.root)
        popup.title(f"Edit Job #{job_id}")
        popup.geometry("400x350")

        jobnum_var = tk.StringVar(value=jobnum)
        vin_var = tk.StringVar(value=vin)
        tech_var = tk.StringVar(value=technician)

        tk.Label(popup, text="Job Number:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Entry(popup, textvariable=jobnum_var).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(popup, text="VIN:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        tk.Entry(popup, textvariable=vin_var).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(popup, text="Technician:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        tech_dropdown = ttk.Combobox(popup, textvariable=tech_var, values=self.tech_list, state="readonly")
        tech_dropdown.grid(row=2, column=1, padx=5, pady=5)
        tech_dropdown.bind("<<ComboboxSelected>>",
            lambda e: self.add_new_technician_for_popup(tech_dropdown, tech_var))

        tk.Label(popup, text="Date:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except:
            date_obj = datetime.today().date()
        date_picker = DateEntry(popup, width=12, background="darkblue", foreground="white")
        date_picker.set_date(date_obj)
        date_picker.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(popup, text="Description:").grid(row=4, column=0, padx=5, pady=5, sticky="nw")
        desc_text = tk.Text(popup, height=5, width=30)
        desc_text.grid(row=4, column=1, padx=5, pady=5)
        desc_text.insert("1.0", description)

        def save_changes():
            conn = sqlite3.connect("worklogs.db")
            cursor = conn.cursor()
            if not jobnum_var.get().isdigit() or len(jobnum_var.get()) > 5:
                messagebox.showerror("Invalid Job Number", "Job number must be numeric and up to 5 digits.")
                return
            if len(vin_var.get()) != 17 or not vin_var.get().isalnum():
                messagebox.showerror("Invalid VIN", "VIN must be exactly 17 alphanumeric characters.")
                return

            cursor.execute("""
                UPDATE logs
                SET jobnum=?, vin=?, technician=?, description=?, date=?
                WHERE id=?
            """, (
                jobnum_var.get(),
                vin_var.get(),
                tech_var.get(),
                desc_text.get("1.0", "end-1c"),
                date_picker.get(),
                job_id
            ))
            conn.commit()
            conn.close()
            self.load_logs()
            popup.destroy()
            messagebox.showinfo("Success", f"Job #{job_id} updated successfully!")

        tk.Button(popup, text="Save Changes", command=save_changes).grid(row=5, column=0, columnspan=2, pady=10)

# --------------------------
# Run App
# --------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = WorkLogApp(root)
    root.mainloop()
