<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>

<h1>🛠️ Automotive Work Log App (Firestore)</h1>

<p>A Python desktop application for managing automotive work logs with Firestore. Track jobs, technicians, status, and dates with a simple, user-friendly interface.</p>

<h2>🚀 Features</h2>
<ul>
    <li>Add, edit, delete work logs</li>
    <li>Track:
        <ul>
            <li>Job Number</li>
            <li>VIN</li>
            <li>Technician</li>
            <li>Status (Pending / In Progress / Complete)</li>
            <li>Description</li>
            <li>Date</li>
        </ul>
    </li>
    <li>Data handling - VINs must be 17 alphanumeric characters & Job number must be a 5 digit number
    <li>Filter and search logs by any field</li>
    <li>Sort columns directly in the logs table</li>
    <li>Export logs to CSV</li>
    <li>Manage technicians (add new technicians)</li>
</ul>

<h2>📸 Screenshots</h2>
<p><strong>Main Form:</strong></p>
<img src="screenshots/main_form.png" alt="Main Form" class="screenshot">

<p><strong>View Logs:</strong></p>
<img src="screenshots/view_logs.png" alt="View Logs" class="screenshot">

<p><strong>Manage Technicians:</strong></p>
<img src="screenshots/manage_technicians.png" alt="View Logs" class="screenshot">
<h2>⚡ Quick Start</h2>
<ol>
    <li>
        <strong>Clone the repo</strong>
        <pre>git clone https://github.com/yourusername/automotive-work-log-app.git
cd automotive-work-log-app</pre>
    </li>
    <li>
        <strong>Install dependencies</strong>
        <pre>pip install tk tkcalendar firebase-admin</pre>
    </li>
    <li>
        <strong>Configure Firebase</strong>
        <ul>
            <li>Create a Firebase project and enable Firestore</li>
            <li>Generate a service account JSON file</li>
            <li>Save it as <code>serviceAccount.json</code> in the project folder</li>
        </ul>
    </li>
    <li>
        <strong>Run the app</strong>
        <pre>python main_firestore.py</pre>
    </li>
</ol>

<h2>📝 Usage</h2>
<ul>
    <li><strong>Add a job:</strong> Fill all fields → <code>Save Entry</code></li>
    <li><strong>View logs:</strong> Click <code>View Job Logs</code> → filter or sort → <code>Search</code></li>
    <li><strong>Edit a job:</strong> Double-click a row or select → <code>Edit Selected</code></li>
    <li><strong>Delete a job:</strong> Select a row → <code>Delete Selected</code></li>
    <li><strong>Export CSV:</strong> Click <code>Export CSV</code> in logs view</li>
</ul>

<h2>⚙️ Requirements</h2>
<ul>
    <li>Python 3.10+</li>
    <li>Tkinter</li>
    <li>tkcalendar</li>
    <li>Firebase Admin SDK</li>
</ul>

<h2>🛠️ Project Structure</h2>
<pre>
/automotive-work-log-app
│
├─ main_firestore.py       # Main application
├─ serviceAccount.json    # Firebase credentials
├─ README.md              # This file
└─ screenshots/           # Screenshots of application
</pre>

<h2>📄 License</h2>
<p>MIT License</p>

</body>
</html>
