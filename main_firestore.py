import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import csv
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# --------------------------
# Firebase Setup
# --------------------------
cred = credentials.Certificate("serviceAccount.json")  # Put your JSON here
firebase_admin.initialize_app(cred)
db = firestore.client()

class WorkLogApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Work Log App (Firestore)")
        self.root.geometry("1000x650")

        # Input variables
        self.jobnum_input = tk.StringVar(value=self.get_next_jobnum())
        self.vin_input = tk.StringVar()
        self.tech_input = tk.StringVar(value="Select...")
        self.status_input = tk.StringVar(value="Pending")
        self.date_var = tk.StringVar(value=datetime.today().strftime("%Y-%m-%d"))

        # UI
        self.create_input_section()
        self.create_buttons()

        # Browser window
        self.browser_window = None

        # Load technicians
        self.load_technicians()

    # --------------------------
    # Input Section
    # --------------------------
    def create_input_section(self):
        frame = tk.LabelFrame(self.root, text="Job Data")
        frame.pack(padx=10, pady=10, fill="x")

        # Job Number
        tk.Label(frame, text="Job Number:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        tk.Entry(frame, textvariable=self.jobnum_input, width=20).grid(row=0, column=1, padx=5, pady=5)

        # VIN
        tk.Label(frame, text="VIN:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        tk.Entry(frame, textvariable=self.vin_input, width=20).grid(row=0, column=3, padx=5, pady=5)

        # Technician
        tk.Label(frame, text="Technician:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.tech_dropdown = ttk.Combobox(frame, textvariable=self.tech_input, state="readonly", width=18)
        self.tech_dropdown.grid(row=1, column=1, padx=5, pady=5)
        self.tech_dropdown.set("Select...")
        self.tech_dropdown.bind("<<ComboboxSelected>>", lambda e: self.add_new_technician_popup(self.tech_dropdown, self.tech_input))

        # Status
        tk.Label(frame, text="Status:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.status_dropdown = ttk.Combobox(frame, textvariable=self.status_input, state="readonly", width=18)
        self.status_dropdown.grid(row=1, column=3, padx=5, pady=5)
        self.status_dropdown["values"] = ["Pending", "In Progress", "Complete"]

        # Date
        tk.Label(frame, text="Date:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.date_button = tk.Button(frame, textvariable=self.date_var, command=self.date_entry, width=15)
        self.date_button.grid(row=2, column=1, padx=5, pady=5)

        # Description
        tk.Label(self.root, text="Job Description:").pack(anchor="w", padx=12)
        self.jobdesc_input = tk.Text(self.root, height=5)
        self.jobdesc_input.pack(padx=10, pady=5, fill="x")

    # --------------------------
    # Buttons
    # --------------------------
    def create_buttons(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10)
        tk.Button(frame, text="Save Entry", command=self.save_job).grid(row=0, column=0, padx=10)
        tk.Button(frame, text="Reset", command=self.reset_form).grid(row=0, column=1, padx=10)
        tk.Button(frame, text="View Job Logs", command=self.view_logs).grid(row=0, column=2, padx=10)
        tk.Button(self.root, text="Manage Technicians", command=self.manage_technicians).pack(pady=5)

    # --------------------------
    # Load Technicians
    # --------------------------
    def load_technicians(self):
        docs = db.collection("technicians").stream()
        self.tech_list = [doc.to_dict()["name"] for doc in docs]
        self.tech_list.append("Add new…")
        if hasattr(self, "tech_dropdown"):
            self.tech_dropdown["values"] = self.tech_list

    def add_new_technician_popup(self, combobox, var):
        if var.get() != "Add new…":
            return
        popup = tk.Toplevel(self.root)
        popup.title("Add Technician")
        popup.geometry("250x120")

        tk.Label(popup, text="Enter new technician name:").pack(pady=5)
        new_name_var = tk.StringVar()
        tk.Entry(popup, textvariable=new_name_var).pack(pady=5)

        def save_name():
            name = new_name_var.get().strip()
            if name and name not in self.tech_list:
                db.collection("technicians").add({"name": name})
                self.load_technicians()
                var.set(name)
            popup.destroy()

        tk.Button(popup, text="Save", command=save_name).pack(pady=5)

    # --------------------------
    # Manage Technicians
    # --------------------------
    def manage_technicians(self):
        tech_window = tk.Toplevel(self.root)
        tech_window.title("Manage Technicians")
        tech_window.geometry("400x400")

        # Treeview for technicians
        columns = ("name", "job_count")
        tree = ttk.Treeview(tech_window, columns=columns, show="headings")
        tree.heading("name", text="Technician Name")
        tree.heading("job_count", text="Assigned Jobs")
        tree.column("name", width=200)
        tree.column("job_count", width=100)
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        def load_techs():
            for row in tree.get_children():
                tree.delete(row)
            docs = db.collection("technicians").stream()
            for doc in docs:
                name = doc.to_dict().get("name", "")
                # Count assigned jobs
                job_count = len(list(db.collection("logs").where("technician", "==", name).stream()))
                tree.insert("", "end", iid=doc.id, values=(name, job_count))

        # Buttons
        btn_frame = tk.Frame(tech_window)
        btn_frame.pack(pady=5)

        def add_tech():
            popup = tk.Toplevel(tech_window)
            popup.title("Add Technician")
            tk.Label(popup, text="Technician Name:").pack(pady=5)
            name_var = tk.StringVar()
            tk.Entry(popup, textvariable=name_var).pack(pady=5)
            def save():
                name = name_var.get().strip()
                if name:
                    db.collection("technicians").add({"name": name})
                    load_techs()
                    self.load_technicians()
                popup.destroy()
            tk.Button(popup, text="Save", command=save).pack(pady=5)

        def edit_tech():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select", "Please select a technician to edit.")
                return
            doc_id = selected[0]
            old_name = tree.item(doc_id)["values"][0]
            popup = tk.Toplevel(tech_window)
            popup.title("Edit Technician")
            tk.Label(popup, text="New Name:").pack(pady=5)
            name_var = tk.StringVar(value=old_name)
            tk.Entry(popup, textvariable=name_var).pack(pady=5)
            def save():
                new_name = name_var.get().strip()
                if new_name and new_name != old_name:
                    # Update tech document
                    db.collection("technicians").document(doc_id).update({"name": new_name})
                    # Update assigned jobs
                    docs = db.collection("logs").where("technician", "==", old_name).stream()
                    for job in docs:
                        db.collection("logs").document(job.id).update({"technician": new_name})
                    load_techs()
                    self.load_technicians()
                popup.destroy()
            tk.Button(popup, text="Save", command=save).pack(pady=5)

        def delete_tech():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select", "Please select a technician to delete.")
                return
            doc_id = selected[0]
            name = tree.item(doc_id)["values"][0]
            # Check if assigned jobs exist
            job_count = len(list(db.collection("logs").where("technician", "==", name).stream()))
            if job_count > 0:
                messagebox.showerror("Cannot Delete", f"{name} has {job_count} assigned jobs.")
                return
            if messagebox.askyesno("Delete", f"Delete technician {name}?"):
                db.collection("technicians").document(doc_id).delete()
                load_techs()
                self.load_technicians()

        tk.Button(btn_frame, text="Add Technician", command=add_tech).grid(row=0,column=0, padx=5)
        tk.Button(btn_frame, text="Edit Technician", command=edit_tech).grid(row=0,column=1, padx=5)
        tk.Button(btn_frame, text="Delete Technician", command=delete_tech).grid(row=0,column=2, padx=5)

        load_techs()


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
    # Save Job
    # --------------------------
    def save_job(self):
        jobnum = self.jobnum_input.get().strip()
        vin = self.vin_input.get().strip()
        tech = self.tech_input.get()
        status = self.status_input.get()
        desc = self.jobdesc_input.get("1.0","end-1c").strip()
        date = self.date_var.get()

        # Validation
        if not jobnum or not vin or not tech or not desc:
            messagebox.showerror("Error", "All fields are required.")
            return
        if not jobnum.isdigit() or len(jobnum) > 5:
            messagebox.showerror("Invalid Job Number", "Job number must be numeric and ≤5 digits.")
            return
        if len(vin) != 17 or not vin.isalnum():
            messagebox.showerror("Invalid VIN", "VIN must be 17 alphanumeric characters.")
            return

        # Check duplicate jobnum
        if db.collection("logs").document(jobnum).get().exists:
            messagebox.showerror("Duplicate Job Number", f"Job #{jobnum} already exists.")
            return

        db.collection("logs").document(jobnum).set({
            "jobnum": jobnum,
            "vin": vin,
            "technician": tech,
            "description": desc,
            "date": date,
            "status": status
        })

        messagebox.showinfo("Success", f"Job #{jobnum} added!")
        self.reset_form()
        if self.browser_window:
            self.load_logs()

    # --------------------------
    # Reset form
    # --------------------------
    def reset_form(self):
        self.jobnum_input.set(self.get_next_jobnum())
        self.vin_input.set("")
        self.tech_input.set("Select...")
        self.status_input.set("Pending")
        self.date_var.set(datetime.today().strftime("%Y-%m-%d"))
        self.jobdesc_input.delete("1.0","end")

    # --------------------------
    # View logs
    # --------------------------
    def view_logs(self):
        if self.browser_window:
            self.browser_window.destroy()

        self.browser_window = tk.Toplevel(self.root)
        self.browser_window.title("Work Log Viewer (Firestore)")
        self.browser_window.geometry("1100x600")

        # Search frame
        search_frame = tk.Frame(self.browser_window)
        search_frame.pack(padx=5, pady=5, fill="x")

        tk.Label(search_frame, text="Job #:").grid(row=0,column=0)
        self.search_jobnum = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_jobnum,width=10).grid(row=0,column=1)

        tk.Label(search_frame, text="VIN:").grid(row=0,column=2)
        self.search_vin = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_vin,width=12).grid(row=0,column=3)

        tk.Label(search_frame, text="Tech:").grid(row=0,column=4)
        self.search_tech = tk.StringVar()
        tk.Entry(search_frame,textvariable=self.search_tech,width=12).grid(row=0,column=5)

        tk.Label(search_frame, text="Status:").grid(row=0,column=6)
        self.search_status = tk.StringVar()
        ttk.Combobox(search_frame, textvariable=self.search_status, values=["","Pending","In Progress","Complete"], width=12, state="readonly").grid(row=0,column=7)

        tk.Label(search_frame, text="Date:").grid(row=0,column=8)
        self.search_date = tk.StringVar()
        DateEntry(search_frame, textvariable=self.search_date, width=12, background="darkblue", foreground="white").grid(row=0,column=9)

        tk.Button(search_frame,text="Search",command=self.load_logs).grid(row=0,column=10, padx=5)
        tk.Button(search_frame,text="Clear",command=self.clear_search).grid(row=0,column=11, padx=5)

        # Treeview
        self.columns = ("id","jobnum","vin","technician","status","description","date")
        self.tree = ttk.Treeview(self.browser_window, columns=self.columns, show="headings")
        self.tree.pack(fill="both", expand=True)
        for col in self.columns:
            width = 300 if col=="description" else 120
            self.tree.heading(col, text=col.title(), command=lambda c=col: self.sort_column(c, False))
            self.tree.column(col, width=width)

        # Buttons
        btn_frame = tk.Frame(self.browser_window)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Refresh", command=self.load_logs).grid(row=0,column=0,padx=5)
        tk.Button(btn_frame, text="Delete Selected", command=self.delete_job).grid(row=0,column=1,padx=5)
        tk.Button(btn_frame, text="Edit Selected", command=self.edit_selected_job).grid(row=0,column=2,padx=5)
        tk.Button(btn_frame,text="Export CSV",command=self.export_csv).grid(row=0,column=3,padx=5)

        self.tree.bind("<Double-1>", self.edit_selected_job)
        self.load_logs()

    # --------------------------
    # Sort column
    # --------------------------
    def sort_column(self, col, reverse):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        if col in ["jobnum"]:
            l.sort(key=lambda t: int(t[0]) if t[0].isdigit() else 0, reverse=reverse)
        else:
            l.sort(reverse=reverse)
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))

    # --------------------------
    # Load logs
    # --------------------------
    def load_logs(self):
        if not hasattr(self, "tree"): return
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Get filters
        jobnum_filter = self.search_jobnum.get().strip() if hasattr(self,"search_jobnum") else ""
        vin_filter = self.search_vin.get().strip() if hasattr(self,"search_vin") else ""
        tech_filter = self.search_tech.get().strip() if hasattr(self,"search_tech") else ""
        status_filter = self.search_status.get().strip() if hasattr(self,"search_status") else ""
        date_filter = self.search_date.get() if hasattr(self,"search_date") and self.search_date.get() else ""

        docs = db.collection("logs").stream()
        for doc in docs:
            data = doc.to_dict()
            match = (
                jobnum_filter.lower() in data.get("jobnum","").lower() and
                vin_filter.lower() in data.get("vin","").lower() and
                tech_filter.lower() in data.get("technician","").lower()
            )
            if status_filter:
                match = match and data.get("status","") == status_filter
            if date_filter:
                match = match and data.get("date","") == date_filter
            if match:
                self.tree.insert("", "end", iid=doc.id, values=(
                    doc.id,
                    data.get("jobnum",""),
                    data.get("vin",""),
                    data.get("technician",""),
                    data.get("status",""),
                    data.get("description",""),
                    data.get("date","")
                ))

    # --------------------------
    # Clear search
    # --------------------------
    def clear_search(self):
        self.search_jobnum.set("")
        self.search_vin.set("")
        self.search_tech.set("")
        self.search_status.set("")
        self.search_date.set("")
        self.load_logs()

    # --------------------------
    # Edit job
    # --------------------------
    def edit_selected_job(self, event=None):
        if not hasattr(self, "tree") or not self.tree or not self.tree.winfo_exists(): return
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a job to edit.")
            return

        doc_id = selected[0]
        doc_ref = db.collection("logs").document(doc_id)
        doc_data = doc_ref.get()
        if not doc_data.exists:
            messagebox.showerror("Error", "Selected job does not exist anymore.")
            self.load_logs()
            return
        data = doc_data.to_dict()

        popup = tk.Toplevel(self.root)
        popup.title(f"Edit Job #{data['jobnum']}")
        popup.geometry("450x400")

        jobnum_var = tk.StringVar(value=data.get("jobnum",""))
        vin_var = tk.StringVar(value=data.get("vin",""))
        tech_var = tk.StringVar(value=data.get("technician",""))
        status_var = tk.StringVar(value=data.get("status","Pending"))

        tk.Label(popup, text="Job Number:").grid(row=0,column=0, padx=5,pady=5, sticky="w")
        tk.Entry(popup, textvariable=jobnum_var).grid(row=0,column=1, padx=5,pady=5)

        tk.Label(popup, text="VIN:").grid(row=1,column=0, padx=5,pady=5, sticky="w")
        tk.Entry(popup, textvariable=vin_var).grid(row=1,column=1, padx=5,pady=5)

        tk.Label(popup, text="Technician:").grid(row=2,column=0, padx=5,pady=5, sticky="w")
        tech_dropdown = ttk.Combobox(popup, textvariable=tech_var, values=self.tech_list, state="readonly")
        tech_dropdown.grid(row=2,column=1, padx=5,pady=5)
        tech_dropdown.bind("<<ComboboxSelected>>", lambda e: self.add_new_technician_popup(tech_dropdown, tech_var))

        tk.Label(popup, text="Status:").grid(row=3,column=0, padx=5,pady=5, sticky="w")
        status_dropdown = ttk.Combobox(popup, textvariable=status_var, values=["Pending","In Progress","Complete"], state="readonly")
        status_dropdown.grid(row=3,column=1, padx=5,pady=5)

        tk.Label(popup, text="Date:").grid(row=4,column=0, padx=5,pady=5, sticky="w")
        try:
            initial_date = datetime.strptime(data.get("date",""), "%Y-%m-%d")
        except:
            initial_date = datetime.today()
        date_picker = DateEntry(popup, width=12, background="darkblue", foreground="white")
        date_picker.set_date(initial_date)
        date_picker.grid(row=4,column=1, padx=5,pady=5)

        tk.Label(popup, text="Description:").grid(row=5,column=0, padx=5,pady=5, sticky="nw")
        desc_text = tk.Text(popup, height=5, width=35)
        desc_text.grid(row=5,column=1, padx=5,pady=5)
        desc_text.insert("1.0", data.get("description",""))

        def save_changes():
            new_jobnum = jobnum_var.get().strip()
            vin = vin_var.get().strip()
            tech = tech_var.get().strip()
            status = status_var.get().strip()
            desc = desc_text.get("1.0","end-1c").strip()
            date_str = date_picker.get_date().strftime("%Y-%m-%d")

            if not new_jobnum or not vin or not tech or not desc:
                messagebox.showerror("Error", "All fields are required.")
                return
            if not new_jobnum.isdigit() or len(new_jobnum)>5:
                messagebox.showerror("Invalid Job Number", "Job number must be numeric and ≤5 digits.")
                return
            if len(vin)!=17 or not vin.isalnum():
                messagebox.showerror("Invalid VIN","VIN must be 17 alphanumeric characters.")
                return

            try:
                if new_jobnum != doc_id:
                    if db.collection("logs").document(new_jobnum).get().exists:
                        messagebox.showerror("Duplicate Job Number", f"Job #{new_jobnum} already exists.")
                        return
                    db.collection("logs").document(new_jobnum).set({
                        "jobnum": new_jobnum,
                        "vin": vin,
                        "technician": tech,
                        "description": desc,
                        "date": date_str,
                        "status": status
                    })
                    db.collection("logs").document(doc_id).delete()
                else:
                    db.collection("logs").document(doc_id).update({
                        "vin": vin,
                        "technician": tech,
                        "description": desc,
                        "date": date_str,
                        "status": status
                    })
                self.load_logs()
                popup.destroy()
                messagebox.showinfo("Success", f"Job #{new_jobnum} updated!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update job: {e}")

        tk.Button(popup, text="Save Changes", command=save_changes).grid(row=6,column=0,columnspan=2,pady=10)

    # --------------------------
    # Delete job
    # --------------------------
    def delete_job(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Please select a job to delete.")
            return
        doc_id = selected[0]
        jobnum = self.tree.item(doc_id)["values"][1]
        if messagebox.askyesno("Delete", f"Delete Job #{jobnum}?"):
            try:
                db.collection("logs").document(doc_id).delete()
                messagebox.showinfo("Deleted", f"Job #{jobnum} deleted successfully!")
                self.load_logs()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete job: {e}")

    # --------------------------
    # Export CSV
    # --------------------------
    def export_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
            filetypes=[("CSV files","*.csv")])
        if not file_path: return
        rows = [self.tree.item(child)["values"] for child in self.tree.get_children()]
        if not rows:
            messagebox.showwarning("No Data","No logs to export")
            return
        with open(file_path,"w",newline="",encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(self.columns)
            writer.writerows(rows)
        messagebox.showinfo("Exported", f"{len(rows)} logs exported!")

    # --------------------------
    # Get next jobnum
    # --------------------------
    def get_next_jobnum(self):
        docs = db.collection("logs").stream()
        max_id = max([int(doc.id) for doc in docs if doc.id.isdigit()], default=0)
        return str(max_id + 1)

# --------------------------
# Run App
# --------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = WorkLogApp(root)
    root.mainloop()
