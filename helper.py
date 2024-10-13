""" helper functions """

import os
import random
import requests
import config
import database_manager

def send_verification_code(phone, code):
    '''this function send otp code via sms'''

    print(code)

    url = "https://api.sms.ir/v1/send/verify"
    payload = {
        "mobile": phone,
        "templateId": 100000,  # Replace with your template ID
        "parameters": [
            {"name": "Code", "value": code}
        ]
    }
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': os.environ.get('SMS_API_KEY', '9QK0KHwGH2G2scmOdKA8vEyfLG0ClpWGDcvU71UGUvUt8PvcC7buE39aZ1oOmcpe')  # کلید API شما
    }

    try:

        response = requests.post(url, json=payload, headers=headers, timeout=5)
        response.raise_for_status()
        result = response.json()
        print(f"Send result: {result}")  # Log the result for debugging
        return result['status'] == 1  # بررسی وضعیت

    except requests.RequestException as e:

        print(f"Request failed: {e}")
        return False  # بازگشت False در صورت بروز خطا


def read_user_with_phone(phone):
    '''this function return user with phone number'''

    conn = database_manager.get_db_connection()

    if conn:

        cursor = conn.cursor()
        # تغییر نام جدول به register
        cursor.execute('SELECT phone FROM register WHERE phone = %s', (phone,))
        user = cursor.fetchone()
        cursor.close()  # بستن cursor

        return conn, user

    return False, False

def generate_random_code():
    '''this function make randome otp code'''

    code = random.randint(config.START_POINT_RANDOM_OTP_CODE, config.END_POINT_RANDOM_OTP_CODE)

    return code

def reset_password_user(hashed_password, reset_code_phone):
    '''this function reset user password'''

    conn = database_manager.get_db_connection()

    if conn:

        cursor = conn.cursor()
        cursor.execute("UPDATE register SET password = %s WHERE phone = %s", (hashed_password, reset_code_phone))
        conn.commit()
        cursor.close()

        return conn , True

    return False, False

def register_user(phone, name, lastname, father_name, national_code, email, birth_place, birth_date, hashed_password):
    '''this function register user at basic level'''

    conn = database_manager.get_db_connection()

    if conn:

        cursor = conn.cursor()
        # تغییر نام جدول به register
        cursor.execute('INSERT INTO register (phone, name, last_name, father_name, national_code, email, birth_place, birth_date, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
            (phone, name, lastname, father_name, national_code, email, birth_place, birth_date, hashed_password))

        conn.commit()
        cursor.close()  # بستن cursor

        return conn , True

    return False, False

def read_user_with_national_code(national_code):
    '''this function login things user'''

    conn = database_manager.get_db_connection()

    if conn:

        cursor = conn.cursor()
        # تغییر نام جدول به register
        cursor.execute('SELECT * FROM register WHERE national_code = %s', (national_code,))
        user = cursor.fetchone()
        cursor.close()  # بستن cursor

        return conn, user

    return False, False

def read_user_datas_with_phone(phone):
    '''this function user datas from database'''

    conn = database_manager.get_db_connection()

    if conn:

        cursor = conn.cursor()
        cursor.execute(
            'SELECT national_code, email, name, last_name, father_name, birth_place, birth_date '
            'FROM karjoo.register WHERE phone = %s',
            (phone,)
        )

        result = cursor.fetchone()
        cursor.close()  # بستن cursor
        return conn, result

    return False, False

def read_user_with_phone_from_user(phone):
    '''this function user from database'''

    conn = database_manager.get_db_connection()

    if conn:

        cursor = conn.cursor()
        cursor.execute('SELECT * FROM register WHERE phone = %s', (phone,))
        user_data = cursor.fetchone()
        cursor.close()  # بستن cursor

        return conn, user_data

    return False, False

def update_user_datas_with_phone(name, father_name, email, birth_place, birth_date, phone):
    '''this function update user datas using phone number'''

    conn = database_manager.get_db_connection()

    if conn:

        cursor = conn.cursor()
        cursor.execute('UPDATE register SET name = %s, father_name = %s, email = %s, birth_place = %s, birth_date = %s WHERE phone = %s',
                        (name, father_name, email, birth_place, birth_date, phone))
        conn.commit()
        cursor.close()  # بستن cursor

        return conn , True

    return False, False

def completion_register_user(datas):
    '''this function complete register user datas'''

    conn = database_manager.get_db_connection()

    if conn:

        cursor = conn.cursor()

        # Insert into Personal_Info
        cursor.execute("""
            INSERT INTO Personal_Info (national_code, gender, name, last_name, father_name, birth_date, birth_place)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            datas["national_code"],
            datas["gender"],
            datas["name"],
            datas["last_name"],
            datas["father_name"],
            datas["birth_date"],
            datas["birth_place"]
        ))

        # Insert into Identification_Info
        cursor.execute("""
            INSERT INTO Identification_Info (national_code, email, birth_certificate_number, issuance_place, religion, nationality)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            datas["national_code"],
            datas["email"],
            datas["birth_certificate_number"],
            datas["issuance_place"],
            datas["religion"],
            datas["nationality"]
        ))

        if datas["children_count"] == '':
            datas["children_count"] = 0

        else:

            datas["children_count"] = int(datas["children_count"])

        # Insert into Marital_Health_Status
        cursor.execute("""
            INSERT INTO Marital_Health_Status (national_code, marital_status, children_count, health_status, health_details)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            datas["national_code"],
            datas["marital_status"],
            datas["children_count"],
            datas["health_status"],
            datas["health_details"]
        ))

        datas["gpa"] = float(datas["gpa"])

        # Insert into Education
        cursor.execute("""
            INSERT INTO Education (national_code, last_degree, field_of_study, gpa, graduation_date, university_type, institute_name, city_country)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            datas["national_code"],
            datas["last_degree"],
            datas["field_of_study"],
            datas["gpa"],
            datas["graduation_date"],
            datas["university_type"],
            datas["institute_name"],
            datas["city_country"]
        ))

        # Insert into Work_Experience
        cursor.execute("""
            INSERT INTO Work_Experience (national_code, organization_name, job_title, contact_number, start_date, end_date, last_salary, reason_for_leaving)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            datas["national_code"],
            datas["organization_name"],
            datas["job_title"],
            datas["contact_number"],
            datas["start_date"],
            datas["end_date"],
            datas["last_salary"],
            datas["reason_for_leaving"]
        ))

        # Insert into Language_Computer
        cursor.execute("""
            INSERT INTO Language_Computer (national_code, reading, writing, speaking, computer_skills)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            datas["national_code"],
            datas["english_reading"],
            datas["english_writing"],
            datas["english_speaking"],
            datas["computer_skills"]
        ))

        # Insert into Specialty_Certificates
        cursor.execute("""
            INSERT INTO Specialty_Certificates (national_code, specialty_name)
            VALUES (%s, %s)
        """, (
            datas["national_code"],
            datas["specialty"]
        ))

        # Insert into Work_Preference
        cursor.execute("""
            INSERT INTO Work_Preference (national_code, work_preference, other_details)
            VALUES (%s, %s, %s)
        """, (
            datas["national_code"],
            datas["workPreference"],
            datas["part_time_details"]
        ))

        # Insert into Insurance_Status
        cursor.execute("""
            INSERT INTO Insurance_Status (national_code, insurance_status, insurance_details)
            VALUES (%s, %s, %s)
        """, (
            datas["national_code"],
            datas["insurance_status"],
            datas["insurance_details"]
        ))

        # Insert into Guarantors
        cursor.execute("""
            INSERT INTO Guarantors (national_code, name, relationship, job, address, phone)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            datas["national_code"],
            datas["guarantor_1_name"],
            datas["guarantor_1_relation"],
            datas["guarantor_1_job"],
            datas["guarantor_1_address"],
            datas["guarantor_1_phone"]
        ))

        # Insert into Work_Area
        cursor.execute("""
            INSERT INTO Work_Area (national_code, work_area, preferred_city)
            VALUES (%s, %s, %s)
        """, (
            datas["national_code"],
            datas["workArea"],
            datas["city_country"]
        ))

        # Insert into Military_Service
        cursor.execute("""
            INSERT INTO Military_Service (national_code, service_status, exemption_details)
            VALUES (%s, %s, %s)
        """, (
            datas["national_code"],
            datas["service_status"],
            datas["exemption_details"]
        ))

        # Commit the transactions
        conn.commit()
        cursor.close()

        return conn, True

    return False, False
