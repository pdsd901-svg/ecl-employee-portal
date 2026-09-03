from flask import Flask, render_template, request, redirect, url_for
from database import get_connection
import mysql.connector
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():

    employee_id = request.form.get("employee_id")
    employee_name = request.form.get("employee_name")
    dob = request.form.get("dob")
    gender = request.form.get("gender")
    mobile = request.form.get("mobile")
    email = request.form.get("email")
    department = request.form.get("department")
    designation = request.form.get("designation")
    employee_type = request.form.get("employee_type")
    joining_date = request.form.get("joining_date")

    # NEW FIELDS
    office_building_name = request.form.get("office_building_name")
    floor_no = request.form.get("floor_no")

    address = request.form.get("address")
    district = request.form.get("district")
    state = request.form.get("state")
    pin_code = request.form.get("pin_code")
    emergency_contact = request.form.get("emergency_contact")

    # Basic validation
    if not employee_id or not employee_name:
        return "Employee ID and Employee Name are required."

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        query = """
        INSERT INTO employees (
            employee_id,
            employee_name,
            dob,
            gender,
            mobile,
            email,
            department,
            designation,
            employee_type,
            joining_date,
            office_building_name,
            floor_no,
            address,
            district,
            state,
            pin_code,
            emergency_contact
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s
        )
        """

        values = (
            employee_id,
            employee_name,
            dob or None,
            gender,
            mobile,
            email,
            department,
            designation,
            employee_type,
            joining_date or None,

            # NEW FIELDS
            office_building_name,
            floor_no,

            address,
            district,
            state,
            pin_code,
            emergency_contact
        )

        cursor.execute(query, values)
        connection.commit()

        return redirect(url_for("success"))

    except mysql.connector.IntegrityError:
        return "Error: Employee ID already exists."

    except mysql.connector.Error as error:
        return f"Database Error: {error}"

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

@app.route("/success")
def success():
    return render_template("success.html")


@app.route("/employees")
def employees():

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM employees
            ORDER BY created_at DESC
        """)

        employee_data = cursor.fetchall()

        return render_template(
            "employees.html",
            employees=employee_data
        )

    except mysql.connector.Error as error:

        return f"Database Error: {error}"

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

@app.route("/dashboard")
def dashboard():

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Total employees
        cursor.execute("SELECT COUNT(*) AS total FROM employees")
        total_employees = cursor.fetchone()["total"]

        # Permanent employees
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM employees
            WHERE employee_type = 'Permanent'
        """)
        permanent_employees = cursor.fetchone()["total"]

        # Contract employees
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM employees
            WHERE employee_type = 'Contract'
        """)
        contract_employees = cursor.fetchone()["total"]

        # Trainees
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM employees
            WHERE employee_type = 'Trainee'
        """)
        trainee_employees = cursor.fetchone()["total"]

        # Department-wise employee count
        cursor.execute("""
            SELECT department, COUNT(*) AS total
            FROM employees
            WHERE department IS NOT NULL
            AND department != ''
            GROUP BY department
            ORDER BY total DESC
        """)

        department_data = cursor.fetchall()

        # Recent employees
        cursor.execute("""
            SELECT employee_id,
                   employee_name,
                   department,
                   designation
            FROM employees
            ORDER BY created_at DESC
            LIMIT 5
        """)

        recent_employees = cursor.fetchall()

        return render_template(
            "dashboard.html",
            total_employees=total_employees,
            permanent_employees=permanent_employees,
            contract_employees=contract_employees,
            trainee_employees=trainee_employees,
            department_data=department_data,
            recent_employees=recent_employees
        )

    except mysql.connector.Error as error:
        return f"Database Error: {error}"

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )