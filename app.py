from flask import Flask, request, redirect, url_for, render_template_string
import pymysql

app = Flask(__name__)

db_config = {
    "host": "136.119.35.161",
    "user": "appuser",
    "password": "App123456!",
    "database": "clinic_appointment_db",
    "cursorclass": pymysql.cursors.DictCursor
}

BASE_STYLE = """
<style>
    * {
        box-sizing: border-box;
    }

    body {
        margin: 0;
        font-family: Arial, sans-serif;
        background: #f4f7fb;
        color: #1f2937;
    }

    .topbar {
        background: linear-gradient(90deg, #1e3a8a, #2563eb);
        color: white;
        padding: 18px 36px;
        font-size: 24px;
        font-weight: 700;
        box-shadow: 0 2px 8px rgba(0,0,0,0.12);
    }

    .container {
        max-width: 1200px;
        margin: 32px auto;
        padding: 0 24px 40px;
    }

    .page-title {
        font-size: 48px;
        font-weight: 800;
        margin: 10px 0 18px;
    }

    .subtitle {
        font-size: 18px;
        color: #4b5563;
        margin-bottom: 28px;
    }

    .nav-link {
        display: inline-block;
        margin-bottom: 22px;
        color: #2563eb;
        text-decoration: none;
        font-weight: 600;
    }

    .nav-link:hover {
        text-decoration: underline;
    }

    .button-row {
        display: flex;
        gap: 20px;
        flex-wrap: wrap;
        margin-top: 24px;
    }

    .big-button {
        display: inline-block;
        background: white;
        border: 1px solid #dbe3f0;
        border-radius: 14px;
        padding: 22px 28px;
        min-width: 240px;
        text-decoration: none;
        color: #1f2937;
        box-shadow: 0 4px 14px rgba(0,0,0,0.06);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }

    .big-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 18px rgba(0,0,0,0.10);
    }

    .big-button-title {
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .big-button-desc {
        font-size: 15px;
        color: #6b7280;
    }

    .message-success {
        background: #dcfce7;
        color: #166534;
        border: 1px solid #86efac;
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 18px;
        font-weight: 600;
    }

    .message-error {
        background: #fee2e2;
        color: #991b1b;
        border: 1px solid #fca5a5;
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 18px;
        font-weight: 600;
        max-width: 1000px;
        line-height: 1.5;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 6px 16px rgba(0,0,0,0.06);
    }

    th {
        background: #e8eefb;
        color: #1e3a8a;
        font-size: 16px;
        text-align: left;
        padding: 14px;
        border-bottom: 1px solid #dbe3f0;
    }

    td {
        padding: 14px;
        border-bottom: 1px solid #edf2f7;
        vertical-align: top;
    }

    tr:hover td {
        background: #f8fbff;
    }

    .btn {
        border: none;
        border-radius: 8px;
        padding: 10px 16px;
        font-size: 14px;
        font-weight: 700;
        cursor: pointer;
        transition: opacity 0.15s ease, transform 0.15s ease;
    }

    .btn:hover {
        opacity: 0.92;
        transform: translateY(-1px);
    }

    .btn-primary {
        background: #2563eb;
        color: white;
    }

    .btn-danger {
        background: #dc2626;
        color: white;
    }

    .btn-secondary {
        background: #475569;
        color: white;
    }

    .card {
        background: white;
        border-radius: 14px;
        padding: 28px;
        box-shadow: 0 6px 16px rgba(0,0,0,0.06);
        max-width: 760px;
    }

    .form-grid {
        display: grid;
        grid-template-columns: 180px 1fr;
        gap: 16px 18px;
        align-items: center;
    }

    label {
        font-weight: 700;
        color: #334155;
    }

    input, select {
        width: 100%;
        padding: 10px 12px;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        font-size: 15px;
        background: white;
    }

    input:focus, select:focus {
        outline: none;
        border-color: #2563eb;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
    }

    .form-actions {
        margin-top: 22px;
    }

    .muted {
        color: #6b7280;
        font-size: 14px;
    }
</style>
"""

HOME_HTML = """
<!doctype html>
<html>
<head>
    <title>Clinic Appointment Management System</title>
    """ + BASE_STYLE + """
</head>
<body>
    <div class="topbar">Clinic Appointment Management System</div>

    <div class="container">
        <div class="page-title">Dashboard</div>
        <div class="subtitle">Welcome to our database application. Choose an action below.</div>

        <div class="button-row">
            <a class="big-button" href="{{ url_for('view_appointments') }}">
                <div class="big-button-title">View Appointments</div>
                <div class="big-button-desc">Browse existing appointment records in the system.</div>
            </a>

            <a class="big-button" href="{{ url_for('add_appointment') }}">
                <div class="big-button-title">Add Appointment</div>
                <div class="big-button-desc">Create a new appointment using date and time-slot selection.</div>
            </a>
        </div>
    </div>
</body>
</html>
"""

APPOINTMENTS_HTML = """
<!doctype html>
<html>
<head>
    <title>Appointments</title>
    """ + BASE_STYLE + """
</head>
<body>
    <div class="topbar">Clinic Appointment Management System</div>

    <div class="container">
        <div class="page-title">Appointments</div>
        <a class="nav-link" href="{{ url_for('home') }}">← Back to Home</a>

        {% if message %}
            <div class="message-success">{{ message }}</div>
        {% endif %}

        <table>
            <tr>
                <th>ID</th>
                <th>Patient ID</th>
                <th>Provider ID</th>
                <th>Clinic ID</th>
                <th>Start Time</th>
                <th>End Time</th>
                <th>Status</th>
                <th>Action</th>
            </tr>
            {% for row in appointments %}
            <tr>
                <td>{{ row.appointment_id }}</td>
                <td>{{ row.patient_id }}</td>
                <td>{{ row.provider_id }}</td>
                <td>{{ row.clinic_id }}</td>
                <td>{{ row.start_time }}</td>
                <td>{{ row.end_time }}</td>
                <td>{{ row.status }}</td>
                <td>
                    <form method="post" action="{{ url_for('delete_appointment', appointment_id=row.appointment_id) }}" style="display:inline;">
                        <button class="btn btn-danger" type="submit" onclick="return confirm('Delete this appointment?');">
                            Delete
                        </button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

ADD_HTML = """
<!doctype html>
<html>
<head>
    <title>Add Appointment</title>
    """ + BASE_STYLE + """
</head>
<body>
    <div class="topbar">Clinic Appointment Management System</div>

    <div class="container">
        <div class="page-title">Add Appointment</div>
        <a class="nav-link" href="{{ url_for('home') }}">← Back to Home</a>

        {% if message %}
            <div class="message-error">{{ message }}</div>
        {% endif %}

        <div class="card">
            <form method="post">
                <div class="form-grid">
                    <label for="appointment_id">Appointment ID</label>
                    <input type="number" id="appointment_id" name="appointment_id" required>

                    <label for="patient_id">Patient ID</label>
                    <input type="number" id="patient_id" name="patient_id" required>

                    <label for="provider_id">Provider ID</label>
                    <input type="number" id="provider_id" name="provider_id" required>

                    <label for="clinic_id">Clinic ID</label>
                    <input type="number" id="clinic_id" name="clinic_id" required>

                    <label for="appt_date">Date</label>
                    <input type="date" id="appt_date" name="appt_date" required>

                    <label for="time_slot">Time Slot</label>
                    <select id="time_slot" name="time_slot" required>
                        <option value="">-- Select a time slot --</option>
                        <option value="09:00:00|09:30:00">09:00 - 09:30</option>
                        <option value="10:00:00|10:30:00">10:00 - 10:30</option>
                        <option value="11:00:00|11:30:00">11:00 - 11:30</option>
                        <option value="13:00:00|13:30:00">13:00 - 13:30</option>
                        <option value="14:00:00|14:30:00">14:00 - 14:30</option>
                        <option value="15:00:00|15:30:00">15:00 - 15:30</option>
                    </select>

                    <label for="status">Status</label>
                    <select id="status" name="status" required>
                        <option value="scheduled">scheduled</option>
                        <option value="completed">completed</option>
                        <option value="canceled">canceled</option>
                        <option value="no_show">no_show</option>
                    </select>
                </div>

                <div class="form-actions">
                    <button class="btn btn-primary" type="submit">Add Appointment</button>
                </div>

                <p class="muted">Tip: use an unused Appointment ID and valid Patient, Provider, and Clinic IDs.</p>
            </form>
        </div>
    </div>
</body>
</html>
"""

def get_connection():
    return pymysql.connect(**db_config)

@app.route("/")
def home():
    return render_template_string(HOME_HTML)

@app.route("/appointments")
def view_appointments():
    message = request.args.get("message", "")
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT appointment_id, patient_id, provider_id, clinic_id, start_time, end_time, status
                FROM APPOINTMENT
                ORDER BY appointment_id
            """)
            appointments = cursor.fetchall()
        conn.close()
        return render_template_string(APPOINTMENTS_HTML, appointments=appointments, message=message)
    except Exception as e:
        return f"Error loading appointments: {e}"

@app.route("/add", methods=["GET", "POST"])
def add_appointment():
    message = ""

    if request.method == "POST":
        conn = None
        try:
            appointment_id = int(request.form["appointment_id"])
            patient_id = int(request.form["patient_id"])
            provider_id = int(request.form["provider_id"])
            clinic_id = int(request.form["clinic_id"])

            appt_date = request.form["appt_date"]
            time_slot = request.form["time_slot"]
            status = request.form["status"]

            start_clock, end_clock = time_slot.split("|")
            start_time = f"{appt_date} {start_clock}"
            end_time = f"{appt_date} {end_clock}"

            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM APPOINTMENT
                    WHERE provider_id = %s
                    AND start_time = %s
                """, (provider_id, start_time))
                existing = cursor.fetchone()

                if existing:
                    raise Exception("This time slot is already booked for this provider.")

                cursor.execute("""
                    INSERT INTO APPOINTMENT
                    (appointment_id, patient_id, provider_id, clinic_id, start_time, end_time, status, check_in_time, actual_start_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NULL, NULL)
                """, (appointment_id, patient_id, provider_id, clinic_id, start_time, end_time, status))
                conn.commit()

            conn.close()
            return redirect(url_for("view_appointments", message="Appointment added successfully."))

        except Exception as e:
            if conn:
                conn.rollback()
                conn.close()
            message = f"Error: {e}"

    return render_template_string(ADD_HTML, message=message)

@app.route("/delete/<int:appointment_id>", methods=["POST"])
def delete_appointment(appointment_id):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM APPOINTMENT WHERE appointment_id = %s", (appointment_id,))
            conn.commit()
        conn.close()
        return redirect(url_for("view_appointments", message="Appointment deleted successfully."))
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return f"Error deleting appointment: {e}"

if __name__ == "__main__":
    app.run(debug=True)