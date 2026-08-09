from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import pandas as pd

app = FastAPI()

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "students.xlsx")

try:
    df = pd.read_excel(FILE_PATH)
    df.columns = df.columns.str.strip()
except:
    df = pd.DataFrame()

POS_MAP = {
    "ENGLISH": "ENG POS", "MATHS": "MATHS POS", "SCIENCE": "SCI POS",
    "SOCIAL": "SOC POS", "RME": "RME POS", "COMPUTING": "COM POS",
    "CAREER": "CAR POS", "TWI": "TWI POS", "CREATIVE": "CRE POS"
}

# --- TEACHER LIST ---
TEACHERS = {
    "teacher1": {"password": "1234", "must_change": True},
    "mrlee": {"password": "1234", "must_change": True}
}

# --- ADMIN LOGIN ---
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

current_user = {"username": None, "role": None} # role = "admin" or "teacher"

# --- HTML TEMPLATES ---
login_html = """
<!DOCTYPE html>
<html><head><title>DECENCY INT SCHOOL - Login</title>
<style>
body{{font-family:'Segoe UI',Arial;background:linear-gradient(135deg, #004a99, #0066cc);display:flex;justify-content:center;align-items:center;height:100vh;margin:0}}
.container{{background:white;padding:35px;border-radius:15px;width:380px;box-shadow:0 10px 30px rgba(0,0,0,0.2)}}
h2{{color:#004a99;text-align:center;margin-bottom:20px}}
input,button{{padding:12px;margin:10px 0;width:100%;border-radius:8px;border:1px solid #ccc;font-size:15px}}
button{{background:linear-gradient(135deg, #004a99, #0066cc);color:white;border:none;cursor:pointer;font-weight:bold;font-size:16px}}
button:hover{{opacity:0.9}}
.error{{color:red;text-align:center}}
.logo{{text-align:center;font-size:40px;margin-bottom:10px}}
.school-name{{text-align:center;color:#004a99;font-weight:bold;font-size:18px}}
.tabs{{display:flex;margin-bottom:15px}}
.tab{{flex:1;padding:10px;text-align:center;cursor:pointer;background:#eee}}
.tab.active{{background:#004a99;color:white}}
</style></head>
<body><div class="container"><div class="logo">🏫</div>
<div class="school-name">DECENCY INT SCHOOL</div>
<div class="tabs"><div class="tab active" onclick="showTab('teacher')">Teacher</div><div class="tab" onclick="showTab('admin')">Admin</div></div>
<div id="teacher-form">
<h2>Teacher Login</h2>
<form method="post" action="/login"><input type="hidden" name="role" value="teacher">
<label><b>Username:</b></label><input type="text" name="username" required>
<label><b>Password:</b></label><input type="password" name="password" required>
<button type="submit">Login</button></form></div>
<div id="admin-form" style="display:none">
<h2>Admin Login</h2>
<form method="post" action="/login"><input type="hidden" name="role" value="admin">
<label><b>Username:</b></label><input type="text" name="username" required>
<label><b>Password:</b></label><input type="password" name="password" required>
<button type="submit">Login</button></form></div>{error}
<script>
function showTab(tab){{
    document.getElementById('teacher-form').style.display = tab=='teacher'?'block':'none';
    document.getElementById('admin-form').style.display = tab=='admin'?'block':'none';
    document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
    event.target.classList.add('active');
}}
</script></div></body></html>
"""

admin_dashboard_html = """
<!DOCTYPE html>
<html><head><title>Admin Dashboard</title>
<style>
body{{font-family:'Segoe UI',Arial;background:#f0f2f5;padding:20px}}
.container{{background:white;padding:25px;border-radius:12px;max-width:800px;margin:auto}}
h2{{color:#004a99}}
table{{width:100%;border-collapse:collapse;margin-top:15px}}
th,td{{border:1px solid #ddd;padding:10px;text-align:left}}
th{{background:#004a99;color:white}}
.btn{{padding:8px 12px;border:none;border-radius:5px;cursor:pointer;color:white}}
.add-btn{{background:#28a745}}
.del-btn{{background:#dc3545}}
input{{padding:8px;margin:5px;border-radius:5px;border:1px solid #ccc}}
.topbar{{display:flex;justify-content:space-between;margin-bottom:20px}}
</style></head>
<body><div class="container"><div class="topbar"><h2>🔐 Admin Dashboard</h2><a href="/logout"><button class="del-btn">Logout</button></a></div>
<h3>Add New Teacher</h3>
<form method="post" action="/add-teacher">
<input type="text" name="new_username" placeholder="Username" required>
<input type="text" name="new_password" placeholder="Default Password" value="1234" required>
<button type="submit" class="btn add-btn">+ Add Teacher</button></form>{msg}
<h3>Current Teachers</h3>
<table><tr><th>Username</th><th>Status</th><th>Action</th></tr>{teacher_rows}</table>
<p style="color:#666;font-size:13px">Note: Changes reset when server restarts. For permanent save we need a database.</p></div></body></html>
"""

change_pass_html = """
<!DOCTYPE html>
<html><head><title>Change Password</title>
<style>
body{{font-family:'Segoe UI',Arial;background:#f0f2f5;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}}
.container{{background:white;padding:35px;border-radius:15px;width:400px;box-shadow:0 5px 20px rgba(0,0,0,0.1)}}
h2{{color:#004a99;text-align:center}}
input,button{{padding:12px;margin:10px 0;width:100%;border-radius:8px;border:1px solid #ccc;font-size:15px}}
button{{background:#28a745;color:white;border:none;cursor:pointer;font-weight:bold}}
.warning{{background:#fff3cd;padding:10px;border-radius:5px;color:#856404;text-align:center;margin-bottom:15px}}
</style></head>
<body><div class="container"><h2>🔒 Change Your Password</h2>
<div class="warning">First login. Please change your password.</div>
<form method="post" action="/change-password">
<label><b>New Password:</b></label><input type="password" name="new_password" required>
<label><b>Confirm Password:</b></label><input type="password" name="confirm_password" required>
<button type="submit">Update Password</button></form>{error}</div></body></html>
"""

portal_html = """
<!DOCTYPE html>
<html><head><title>DECENCY INT SCHOOL - Result Portal</title>
<style>
body{{font-family:'Segoe UI',Arial;padding:20px;background:#f0f2f5}}
.container{{background:white;padding:0;border-radius:12px;max-width:900px;margin:auto;box-shadow:0 5px 20px rgba(0,0,0,0.1);overflow:hidden}}
.header{{background:linear-gradient(135deg, #004a99, #0066cc);color:white;padding:20px;text-align:center}}
.content{{padding:25px}}.search-box{{background:#f8f9fa;padding:20px;border-radius:10px}}
input,button{{padding:10px;margin:5px 0;width:100%;border-radius:8px;border:1px solid #ddd}}
button{{background:#28a745;color:white;border:none;cursor:pointer;font-weight:bold}}
.print-btn{{background:#17a2b8}}.topbar{{display:flex;justify-content:space-between;align-items:center;padding:10px 25px;background:#e7f1ff}}
table{{width:100%;border-collapse:collapse;margin-top:10px;font-size:14px}}
th,td{{border:1px solid #dee2e6;padding:10px;text-align:center}}
th{{background:#004a99;color:white}}.total-row{{font-weight:bold;background:#fff3cd!important}}
</style></head>
<body><div class="container"><div class="header"><h1>🏫 DECENCY INT SCHOOL</h1><p>Student Result Portal</p></div>
<div class="topbar"><span>Welcome, <b>{username}</b></span><a href="/logout"><button style="background:#dc3545;width:auto;padding:8px 15px">Logout</button></a></div>
<div class="content"><div class="search-box">
<form method="post" action="/search">
<label><b>Enter Index Number:</b></label><input type="text" name="index_number" placeholder="e.g. 001" required>
<button type="submit">🔍 Search Result</button></form></div>{result}</div></div></body></html>
"""

def calculate_class_position(df, student_index):
    score_cols = [col for col in df.columns if col not in ['INDEX NO','STUDENT NAME','CLASS'] and 'POS' not in col]
    df['TOTAL_CALC'] = df[score_cols].apply(pd.to_numeric, errors='coerce').sum(axis=1)
    df = df.sort_values('TOTAL_CALC', ascending=False).reset_index(drop=True)
    df['CLASS_POS'] = df.index + 1
    pos = df[df['INDEX NO'].astype(str) == str(student_index)]['CLASS_POS'].values
    return int(pos[0]) if len(pos) > 0 else "-"

@app.get("/", response_class=HTMLResponse)
def show_login():
    return login_html.format(error="")

@app.post("/login", response_class=HTMLResponse)
def handle_login(role: str = Form(...), username: str = Form(...), password: str = Form(...)):
    if role == "admin":
        if username == ADMIN_USER and password == ADMIN_PASS:
            current_user["username"] = username
            current_user["role"] = "admin"
            return RedirectResponse(url="/admin", status_code=303)
    else: # teacher
        if username in TEACHERS and TEACHERS[username]["password"] == password:
            current_user["username"] = username
            current_user["role"] = "teacher"
            if TEACHERS[username]["must_change"]:
                return change_pass_html.format(error="")
            else:
                return portal_html.format(result="", username=username)

    return login_html.format(error="<p class='error'>Invalid username or password</p>")

@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(msg=""):
    if current_user["role"]!= "admin":
        return RedirectResponse(url="/", status_code=303)

    rows = ""
    for user, data in TEACHERS.items():
        status = "Must Change Password" if data["must_change"] else "Active"
        rows += f"<tr><td>{user}</td><td>{status}</td><td><a href='/delete-teacher/{user}'><button class='btn del-btn'>Delete</button></a></td></tr>"

    return admin_dashboard_html.format(teacher_rows=rows, msg=msg)

@app.post("/add-teacher", response_class=HTMLResponse)
def add_teacher(new_username: str = Form(...), new_password: str = Form(...)):
    if new_username in TEACHERS:
        return admin_dashboard(msg="<p style='color:red'>Teacher already exists</p>")
    TEACHERS[new_username] = {"password": new_password, "must_change": True}
    return admin_dashboard(msg="<p style='color:green'>Teacher added successfully!</p>")

@app.get("/delete-teacher/{username}")
def delete_teacher(username: str):
    if username in TEACHERS:
        del TEACHERS[username]
    return RedirectResponse(url="/admin", status_code=303)

@app.post("/change-password", response_class=HTMLResponse)
def change_password(new_password: str = Form(...), confirm_password: str = Form(...)):
    username = current_user["username"]
    if new_password!= confirm_password:
        return change_pass_html.format(error="<p class='error'>Passwords do not match</p>")
    TEACHERS[username]["password"] = new_password
    TEACHERS[username]["must_change"] = False
    return portal_html.format(result="", username=username)

@app.get("/logout")
def logout():
    current_user["username"] = None
    current_user["role"] = None
    return RedirectResponse(url="/", status_code=303)

@app.post("/search", response_class=HTMLResponse)
def search_student(index_number: str = Form(...)):
    username = current_user["username"]
    if current_user["role"]!= "teacher":
        return RedirectResponse(url="/", status_code=303)

    index_str = str(index_number).zfill(3)
    student = df[df["INDEX NO"].astype(str).str.zfill(3) == index_str]
    if student.empty:
        return portal_html.format(result="<h3 style='color:red;text-align:center'>No student found</h3>", username=username)

    s = student.iloc[0]
    class_pos = calculate_class_position(df.copy(), s['INDEX NO'])
    rows, total_score = "", 0
    for subject, pos_col in POS_MAP.items():
        if subject in df.columns:
            score, pos = s[subject], s[pos_col] if pos_col in df.columns else "-"
            try: total_score += float(score)
            except: pass
            rows += f"<tr><td><b>{subject}</b></td><td>{score}</td><td>{pos}</td></tr>"
    rows += f"<tr class='total-row'><td><b>TOTAL</b></td><td><b>{int(total_score)}</b></td><td>-</td></tr>"

    result_html = f"""<div><div class="header"><h1>DECENCY INT SCHOOL</h1><h2>ACADEMIC RESULT SLIP</h2></div>
    <p><b>Name:</b> {s['STUDENT NAME']} | <b>Index:</b> {s['INDEX NO']} | <b>Class:</b> {s['CLASS']} | <b>Position:</b> {class_pos}</p>
    <table><tr><th>Subject</th><th>Score</th><th>Position</th></tr>{rows}</table>
    <div style="text-align:center;margin-top:20px"><button class="print-btn" onclick="window.print()">🖨️ Print</button></div>
    <p style="text-align:center;font-size:12px;color:#666"><i>This is a computer generated result by Eraser Solution</i></p></div>"""
    return portal_html.format(result=result_html, username=username)
