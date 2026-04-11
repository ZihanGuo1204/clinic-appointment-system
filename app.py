from flask import Flask, request, redirect, url_for, render_template
import pymysql

app = Flask(__name__)

db_config = {
    "host": "136.119.35.161",
    "user": "appuser",
    "password": "App123456!",
    "database": "clinic_appointment_db",
    "cursorclass": pymysql.cursors.DictCursor
}


def get_connection():
    return pymysql.connect(**db_config)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/appointments")
def view_appointments():
    message = request.args.get("message", "")
    error = ""

    appointment_id = request.args.get("appointment_id", "").strip()
    patient_id = request.args.get("patient_id", "").strip()
    provider_id = request.args.get("provider_id", "").strip()
    status = request.args.get("status", "").strip()

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
                SELECT appointment_id, patient_id, provider_id, clinic_id,
                       start_time, end_time, status
                FROM APPOINTMENT
                WHERE 1=1
            """
            params = []

            if appointment_id:
                query += " AND appointment_id = %s"
                params.append(appointment_id)

            if patient_id:
                query += " AND patient_id = %s"
                params.append(patient_id)

            if provider_id:
                query += " AND provider_id = %s"
                params.append(provider_id)

            if status:
                query += " AND status = %s"
                params.append(status)

            query += " ORDER BY appointment_id"

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
            status=status
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
            status=status
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
            status=status
        )


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
                # Prevent double booking for the same provider and start time
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
                    (appointment_id, patient_id, provider_id, clinic_id,
                     start_time, end_time, status, check_in_time, actual_start_time)
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

        except Exception as e:
            if conn:
                conn.rollback()
                conn.close()
            message = f"Error: {e}"

    return render_template("add.html", message=message)


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


if __name__ == "__main__":
    app.run(debug=True)