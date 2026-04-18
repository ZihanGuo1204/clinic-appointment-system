from flask import Flask, request, redirect, url_for, render_template
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "cursorclass": pymysql.cursors.DictCursor
}


def get_connection():
    return pymysql.connect(**db_config)


@app.route("/")
def home():
    message = request.args.get("message", "")
    return render_template("home.html", message=message)


@app.route("/appointments")
def view_appointments():
    message = request.args.get("message", "")
    error = ""

    appointment_id = request.args.get("appointment_id", "").strip()
    patient_id = request.args.get("patient_id", "").strip()
    provider_id = request.args.get("provider_id", "").strip()
    status = request.args.get("status", "").strip()
    sort_by = request.args.get("sort_by", "date_asc").strip()

    try:
        if appointment_id and not appointment_id.isdigit():
            raise ValueError("Appointment ID must be a number.")

        if patient_id and not patient_id.isdigit():
            raise ValueError("Patient ID must be a number.")

        if provider_id and not provider_id.isdigit():
            raise ValueError("Provider ID must be a number.")

        conn = get_connection()
        with conn.cursor() as cursor:
            query = """
                SELECT
                    a.appointment_id,
                    a.patient_id,
                    CONCAT(pe.first_name, ' ', pe.last_name) AS patient_name,
                    a.provider_id,
                    pr.provider_name,
                    a.clinic_id,
                    c.clinic_name,
                    a.start_time,
                    a.end_time,
                    a.status
                FROM APPOINTMENT a
                JOIN PATIENT pa ON a.patient_id = pa.patient_id
                JOIN PERSON pe ON pa.patient_id = pe.person_id
                JOIN PROVIDER pr ON a.provider_id = pr.provider_id
                JOIN CLINIC c ON a.clinic_id = c.clinic_id
                WHERE 1=1
            """
            params = []

            if appointment_id:
                query += " AND a.appointment_id = %s"
                params.append(appointment_id)

            if patient_id:
                query += " AND a.patient_id = %s"
                params.append(patient_id)

            if provider_id:
                query += " AND a.provider_id = %s"
                params.append(provider_id)

            if status:
                query += " AND a.status = %s"
                params.append(status)

            if sort_by == "date_desc":
                query += " ORDER BY a.start_time DESC"
            elif sort_by == "patient_az":
                query += " ORDER BY pe.first_name ASC, pe.last_name ASC"
            elif sort_by == "provider_az":
                query += " ORDER BY pr.provider_name ASC"
            else:
                query += " ORDER BY a.start_time ASC"

            cursor.execute(query, params)
            appointments = cursor.fetchall()

        conn.close()

        searched = appointment_id or patient_id or provider_id or status
        if searched and not appointments:
            message = "No appointments found matching your search criteria."

        return render_template(
            "appointments.html",
            appointments=appointments,
            message=message,
            error=error,
            appointment_id=appointment_id,
            patient_id=patient_id,
            provider_id=provider_id,
            status=status,
            sort_by=sort_by
        )

    except ValueError as ve:
        error = str(ve)
        return render_template(
            "appointments.html",
            appointments=[],
            message="",
            error=error,
            appointment_id=appointment_id,
            patient_id=patient_id,
            provider_id=provider_id,
            status=status,
            sort_by=sort_by
        )

    except Exception as e:
        error = f"Error loading appointments: {e}"
        return render_template(
            "appointments.html",
            appointments=[],
            message="",
            error=error,
            appointment_id=appointment_id,
            patient_id=patient_id,
            provider_id=provider_id,
            status=status,
            sort_by=sort_by
        )


@app.route("/add", methods=["GET", "POST"])
def add_appointment():
    message = ""
    conn = None

    try:
        conn = get_connection()

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT p.patient_id, pe.first_name, pe.last_name
                FROM PATIENT p
                JOIN PERSON pe ON p.patient_id = pe.person_id
                ORDER BY p.patient_id
            """)
            patients = cursor.fetchall()

            cursor.execute("""
                SELECT provider_id, provider_name
                FROM PROVIDER
                ORDER BY provider_id
            """)
            providers = cursor.fetchall()

            cursor.execute("""
                SELECT clinic_id, clinic_name
                FROM CLINIC
                ORDER BY clinic_id
            """)
            clinics = cursor.fetchall()

        if request.method == "POST":
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

            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT *
                    FROM APPOINTMENT
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
                """, (
                    appointment_id,
                    patient_id,
                    provider_id,
                    clinic_id,
                    start_time,
                    end_time,
                    status
                ))
                conn.commit()

            conn.close()
            return redirect(url_for("view_appointments", message="Appointment added successfully."))

        conn.close()
        return render_template(
            "add.html",
            message=message,
            patients=patients,
            providers=providers,
            clinics=clinics
        )

    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()

        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT p.patient_id, pe.first_name, pe.last_name
                    FROM PATIENT p
                    JOIN PERSON pe ON p.patient_id = pe.person_id
                    ORDER BY p.patient_id
                """)
                patients = cursor.fetchall()

                cursor.execute("""
                    SELECT provider_id, provider_name
                    FROM PROVIDER
                    ORDER BY provider_id
                """)
                providers = cursor.fetchall()

                cursor.execute("""
                    SELECT clinic_id, clinic_name
                    FROM CLINIC
                    ORDER BY clinic_id
                """)
                clinics = cursor.fetchall()
            conn.close()
        except Exception:
            patients, providers, clinics = [], [], []

        return render_template(
            "add.html",
            message=f"Error: {e}",
            patients=patients,
            providers=providers,
            clinics=clinics
        )


@app.route("/add_patient", methods=["GET", "POST"])
def add_patient():
    message = ""
    conn = None

    if request.method == "POST":
        try:
            patient_id = int(request.form["patient_id"])
            first_name = request.form["first_name"].strip()
            last_name = request.form["last_name"].strip()
            email = request.form["email"].strip()

            if not first_name or not last_name or not email:
                raise Exception("All fields are required.")

            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM PERSON WHERE person_id = %s",
                    (patient_id,)
                )
                existing_person = cursor.fetchone()

                if existing_person:
                    raise Exception("This Patient ID already exists.")

                cursor.execute("""
                    INSERT INTO PERSON (person_id, first_name, last_name, email)
                    VALUES (%s, %s, %s, %s)
                """, (patient_id, first_name, last_name, email))

                cursor.execute("""
                    INSERT INTO PATIENT (patient_id)
                    VALUES (%s)
                """, (patient_id,))

                conn.commit()

            conn.close()
            return redirect(url_for("home", message="Patient added successfully."))

        except Exception as e:
            if conn:
                conn.rollback()
                conn.close()
            message = f"Error: {e}"

    return render_template("add_patient.html", message=message)


@app.route("/delete/<int:appointment_id>", methods=["POST"])
def delete_appointment(appointment_id):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM APPOINTMENT WHERE appointment_id = %s",
                (appointment_id,)
            )
            conn.commit()
        conn.close()

        return redirect(url_for("view_appointments", message="Appointment deleted successfully."))
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return f"Error deleting appointment: {e}"


@app.route("/update/<int:appointment_id>", methods=["GET", "POST"])
def update_appointment(appointment_id):
    conn = None
    try:
        conn = get_connection()

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT p.patient_id, pe.first_name, pe.last_name
                FROM PATIENT p
                JOIN PERSON pe ON p.patient_id = pe.person_id
                ORDER BY p.patient_id
            """)
            patients = cursor.fetchall()

            cursor.execute("""
                SELECT provider_id, provider_name
                FROM PROVIDER
                ORDER BY provider_id
            """)
            providers = cursor.fetchall()

            cursor.execute("""
                SELECT clinic_id, clinic_name
                FROM CLINIC
                ORDER BY clinic_id
            """)
            clinics = cursor.fetchall()

        if request.method == "POST":
            patient_id = int(request.form["patient_id"])
            provider_id = int(request.form["provider_id"])
            clinic_id = int(request.form["clinic_id"])
            appt_date = request.form["appt_date"]
            time_slot = request.form["time_slot"]
            status = request.form["status"].strip()

            if status not in ["scheduled", "completed", "canceled", "no_show"]:
                raise Exception("Invalid status selected.")

            start_clock, end_clock = time_slot.split("|")
            start_time = f"{appt_date} {start_clock}"
            end_time = f"{appt_date} {end_clock}"

            #double checking
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT *
                    FROM APPOINTMENT
                    WHERE provider_id = %s
                      AND start_time = %s
                      AND appointment_id <> %s
                """, (provider_id, start_time, appointment_id))
                existing = cursor.fetchone()

                if existing:
                    raise Exception("This time slot is already booked for this provider.")

                cursor.execute("""
                    UPDATE APPOINTMENT
                    SET patient_id = %s,
                        provider_id = %s,
                        clinic_id = %s,
                        start_time = %s,
                        end_time = %s,
                        status = %s
                    WHERE appointment_id = %s
                """, (
                    patient_id,
                    provider_id,
                    clinic_id,
                    start_time,
                    end_time,
                    status,
                    appointment_id
                ))
                conn.commit()

            conn.close()
            return redirect(url_for("view_appointments", message="Appointment updated successfully."))

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT appointment_id, patient_id, provider_id, clinic_id,
                       start_time, end_time, status
                FROM APPOINTMENT
                WHERE appointment_id = %s
            """, (appointment_id,))
            appointment = cursor.fetchone()

        conn.close()

        if not appointment:
            return redirect(url_for("view_appointments", message="Appointment not found."))

        appt_date = appointment["start_time"].strftime("%Y-%m-%d")
        start_clock = appointment["start_time"].strftime("%H:%M:%S")
        end_clock = appointment["end_time"].strftime("%H:%M:%S")
        current_time_slot = f"{start_clock}|{end_clock}"

        return render_template(
            "update_appointment.html",
            appointment=appointment,
            patients=patients,
            providers=providers,
            clinics=clinics,
            appt_date=appt_date,
            current_time_slot=current_time_slot
        )

    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return f"Error updating appointment: {e}"


if __name__ == "__main__":
    app.run(debug=True)