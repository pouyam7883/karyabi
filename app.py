from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
import random
import requests
import time
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')


    

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="788303",
            database="karjoo"
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to database: {e}")
        return None
    

    
    
    
def send_verification_code(phone, code):
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
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        print(f"Send result: {result}")  # Log the result for debugging
        return result['status'] == 1  # بررسی وضعیت
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return False  # بازگشت False در صورت بروز خطا





@app.route('/')
def index():
    return render_template('index.html')


@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        data = request.json
        phone = data.get('phone')
        code = data.get('code')
        resend = data.get('resend', False)

        if code:
            # Code verification
            code_sent_time = session.get('code_time', 0)
            if 'code' in session and code.isdigit():
                if int(code) == session.get('code'):
                    if time.time() - code_sent_time <= 120:
                        conn = get_db_connection()
                        if conn:
                            try:
                                cursor = conn.cursor()
                                # تغییر نام جدول به register
                                cursor.execute('SELECT phone FROM register WHERE phone = %s', (phone,))
                                user = cursor.fetchone()
                                cursor.close()  # بستن cursor
                                conn.close()  # بستن اتصال
                                
                                if user:
                                    return jsonify({'success': True, 'redirect': url_for('login')})
                                else:
                                    return jsonify({'success': True, 'redirect': url_for('register')})
                            except mysql.connector.Error as e:
                                print(f"Database error: {e}")
                                return jsonify({'success': False, 'error': 'خطای پایگاه داده'})
                        else:
                            return jsonify({'success': False, 'error': 'خطا در اتصال به پایگاه داده'})
                    else:
                        return jsonify({'success': False, 'error': 'کد تایید منقضی شده است'})
                else:
                    return jsonify({'success': False, 'error': 'کد تایید نادرست است'})
            else:
                return jsonify({'success': False, 'error': 'کد تایید معتبر نیست. لطفاً دوباره تلاش کنید.'})
        elif phone:
            # Phone number submission or resend code
            code = random.randint(1000, 9999)
            send_verification_code(phone, code)
            session['phone'] = phone
            session['code'] = code
            session['code_time'] = time.time()
            return jsonify({'success': True})
        
    return render_template('auth.html')



@app.route('/send_code', methods=['POST'])
def send_code():
    data = request.get_json()
    phone = data.get('phone')
    if phone:
        code = random.randint(1000, 9999)
        result = send_verification_code(phone, code)
        if result.get('success'):
            session['reset_code'] = code
            session['reset_code_phone'] = phone
            session['code_time'] = time.time()  # Save the time when code was sent
            return jsonify({'success': True})
    return jsonify({'success': False})


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        data = request.json
        phone = data.get('phone')
        code = data.get('code')
        new_password = data.get('newPassword')
        confirm_password = data.get('confirmPassword')

        if phone and not code:
            # Step 1: Send verification code
            verification_code = str(random.randint(100000, 999999))
            session['reset_code'] = verification_code
            session['reset_code_phone'] = phone
            session['code_time'] = time.time()

            send_result = send_verification_code(phone, verification_code)
            if send_result:
                return jsonify({"success": True, "message": "کد تایید ارسال شد."})
            else:
                return jsonify({"success": False, "error": "خطا در ارسال کد تایید."})

        elif code and new_password and confirm_password:
            # Step 2: Verify code and change password
            if new_password != confirm_password:
                return jsonify({"success": False, "error": "رمز عبور و تکرار آن مطابقت ندارند."})

            if code != session.get('reset_code'):
                return jsonify({"success": False, "error": "کد تایید نادرست است."})

            if time.time() - session.get('code_time', 0) > 120:
                return jsonify({"success": False, "error": "کد تایید منقضی شده است."})

            hashed_password = generate_password_hash(new_password)
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE register SET password = %s WHERE phone = %s", (hashed_password, session['reset_code_phone']))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    session.pop('reset_code', None)
                    session.pop('reset_code_phone', None)
                    session.pop('code_time', None)
                    return jsonify({"success": True, "message": "رمز عبور با موفقیت تغییر کرد."})
                except mysql.connector.Error as e:
                    print(f"Database error: {e}")
                    return jsonify({"success": False, "error": "خطا در تغییر رمز عبور."})
            else:
                return jsonify({"success": False, "error": "خطا در اتصال به پایگاه داده."})

    return render_template('reset_password.html')




@app.route('/resend_reset_code', methods=['POST'])
def resend_reset_code():
    phone = session.get('reset_code_phone')
    if phone:
        verification_code = str(random.randint(100000, 999999))
        session['reset_code'] = verification_code
        session['code_time'] = time.time()

        send_result = send_verification_code(phone, verification_code)
        if send_result:
            return jsonify({"success": True, "message": "کد تایید مجدداً ارسال شد."})
        else:
            return jsonify({"success": False, "error": "خطا در ارسال مجدد کد تایید."})
    else:
        return jsonify({"success": False, "error": "شماره تلفن در جلسه ذخیره نشده است."})



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone = session.get('phone')
        name = request.form['name']
        lastname = request.form['lastname']
        fatherName = request.form['fatherName']
        nationalCode = request.form['nationalCode']
        email = request.form['email']
        birthPlace = request.form['birthPlace']
        birthDate = request.form['birthDate']
        password = request.form['password']
        confirmPassword = request.form['confirmPassword']
        
        if password != confirmPassword:
            return "رمز عبور و تکرار آن با هم مطابقت ندارند"
        
        hashed_password = generate_password_hash(password)  # Hash the password

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # تغییر نام جدول به register
            cursor.execute('INSERT INTO register (phone, name, last_name, father_name, national_code, email, birth_place, birth_date, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', 
               (phone, name, lastname, fatherName, nationalCode, email, birthPlace, birthDate, hashed_password))

            conn.commit()
            cursor.close()  # بستن cursor
            conn.close()  # بستن اتصال
        except mysql.connector.Error as e:
            print(f"Database error: {e}")
            return "خطای پایگاه داده"
        
        # ذخیره کد ملی و رمز عبور در session
        session['user'] = {
            'national_code': nationalCode,
            'password': password  # می‌توانید رمز عبور را در session ذخیره کنید
        }
        
        return redirect(url_for('success'))
    
    return render_template('register.html')



@app.route('/success')
def success():
    user = session.get('user', {})
    user_name = user.get('name', 'کاربر')
    return render_template('success.html', user_name=user_name)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None
    forgot_password = False
    
    if request.method == 'POST':
        national_code = request.form['national_code']
        password = request.form['password']
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # تغییر نام جدول به register
            cursor.execute('SELECT * FROM register WHERE national_code = %s', (national_code,))
            user = cursor.fetchone()
            cursor.close()  # بستن cursor
            conn.close()  # بستن اتصال
            
            if user:
                # فرض بر این است که password در ایندکس 8 قرار دارد
                if check_password_hash(user[9], password):  # تغییر ایندکس به 8
                    session['user'] = {'name': user[2], 'phone': user[1]}  # فرض بر این است که index 2 نام و index 1 شماره تلفن است
                    return redirect(url_for('dashboard'))
                else:
                    error_message = "رمز عبور نادرست است."
                    forgot_password = True
            else:
                error_message = "کد کاربری نادرست است."
        except mysql.connector.Error as e:
            print(f"Database error: {e}")
            error_message = "خطای پایگاه داده"
    
    return render_template('login.html', error_message=error_message, forgot_password=forgot_password)



@app.route('/employer')
def employer():
    return render_template('employer.html')


@app.route('/dashboard')
def dashboard():
    user = session.get('user')
    if user:
        return render_template('dashboard.html', user_name=user.get('name', 'کاربر'))
    return redirect(url_for('login'))

@app.route('/search_job')
def search_job():
    return 'صفحه جستجوی شغل'



@app.route('/completion', methods=['GET', 'POST'])
def completion():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))

    user_data = {}
    has_submitted = False
    success_message = None  # برای نمایش پیام موفقیت

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    'SELECT national_code, email, name, last_name, father_name, birth_place, birth_date '
                    'FROM karjoo.register WHERE phone = %s',
                    (user['phone'],)
                )
                result = cursor.fetchone()
                if result:
                    user_data = dict(zip(['national_code', 'email', 'name', 'last_name', 'father_name', 'birth_place', 'birth_date'], result))
                    has_submitted = True
                else:
                    return jsonify({'message': "کاربر یافت نشد."}), 404
    except mysql.connector.Error as e:
        print(f"خطای پایگاه داده karjoo: {e}")
        return jsonify({'message': "خطای پایگاه داده: لطفاً دوباره تلاش کنید."}), 500

    if request.method == 'POST' and not has_submitted:
        form_data = request.form.to_dict()

        # اعتبارسنجی داده‌ها
        required_fields = ['national_code', 'email', 'name', 'last_name', 'father_name', 'birth_date', 'birth_place']
        for field in required_fields:
            if field not in form_data or not form_data[field].strip():
                return jsonify({'message': f"فیلد {field} نمی‌تواند خالی باشد."}), 400

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    tables = [
                        ('Personal_Info', ['national_code', 'gender', 'name', 'last_name', 'father_name', 'birth_date', 'birth_place']),
                        ('Identification_Info', ['national_code', 'email', 'birth_certificate_number', 'issuance_place', 'religion', 'nationality']),
                        ('Marital_Health_Status', ['national_code', 'marital_status', 'children_count', 'health_status', 'health_details']),
                        ('Military_Service', ['national_code', 'service_status', 'exemption_details']),
                        ('Education', ['national_code', 'last_degree', 'field_of_study', 'gpa', 'graduation_date', 'university_type', 'institute_name', 'city_country']),
                        ('Work_Experience', ['national_code', 'organization_name', 'job_title', 'contact_number', 'start_date', 'end_date', 'last_salary', 'reason_for_leaving']),
                        ('Language_Computer', ['national_code', 'reading', 'writing', 'speaking', 'computer_skills']),
                        ('Specialty_Certificates', ['national_code', 'specialty_name']),
                        ('Work_Preference', ['national_code', 'work_preference', 'other_details']),
                        ('Insurance_Status', ['national_code', 'insurance_status', 'insurance_details']),
                        ('Guarantors', ['national_code', 'name', 'relationship', 'job', 'address', 'phone']),
                        ('Work_Area', ['national_code', 'work_area', 'preferred_city'])
                    ]

                    for table, fields in tables:
                        values = [form_data.get(field, '') for field in fields]
                        placeholders = ', '.join(['%s'] * len(fields))
                        query = f'INSERT INTO {table} ({", ".join(fields)}) VALUES ({placeholders})'
                        cursor.execute(query, values)

                conn.commit()

            success_message = "اطلاعات با موفقیت در پایگاه داده ثبت شد."  # پیام موفقیت

        except mysql.connector.Error as e:
            print(f"خطای پایگاه داده karjoo_users: {e}")
            return jsonify({'message': "خطای پایگاه داده: لطفاً دوباره تلاش کنید."}), 500

    site_key = os.environ.get('6LdkmVMqAAAAAG0wgje4UsBRojk3X7HGNDGa5_PC')  # کلید reCAPTCHA باید به درستی تعریف شده باشد
    return render_template('completion.html', user_data=user_data, has_submitted=has_submitted, success_message=success_message, site_key=site_key)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))

    user_data = None
    message = None
    edit_error = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if request.method == 'POST':
            if 'edit' in request.form:
                cursor.execute('SELECT * FROM users WHERE phone = %s', (user['phone'],))
                user_data = cursor.fetchone()
                conn.close()
                return render_template('profile.html', user_data=user_data, editing=True)
            elif 'save' in request.form:
                name = request.form['name']
                father_name = request.form['father_name']
                national_code = request.form['national_code']
                email = request.form['email']
                birth_place = request.form['birth_place']
                birth_date = request.form['birth_date']

                if not all([name, father_name, email, birth_place, birth_date]):
                    edit_error = "لطفاً تمامی فیلدها را پر کنید."
                    return render_template('profile.html', user_data=user_data, editing=True, edit_error=edit_error)

                try:
                    cursor.execute('UPDATE users SET name = %s, father_name = %s, email = %s, birth_place = %s, birth_date = %s WHERE phone = %s',
                                   (name, father_name, email, birth_place, birth_date, user['phone']))
                    conn.commit()

                    cursor.execute('SELECT * FROM users WHERE phone = %s', (user['phone'],))
                    user_data = cursor.fetchone()
                    
                    message = "اطلاعات شما با موفقیت ثبت شد"
                    return render_template('profile.html', user_data=user_data, editing=False, message=message)
                except mysql.connector.Error as e:
                    edit_error = "خطا در ثبت اطلاعات"
                    return render_template('profile.html', user_data=user_data, editing=True, edit_error=edit_error)

            elif 'cancel' in request.form:
                return redirect(url_for('profile'))

        cursor.execute('SELECT * FROM users WHERE phone = %s', (user['phone'],))
        user_data = cursor.fetchone()
        conn.close()

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        edit_error = "خطا در ارتباط با پایگاه داده"

    return render_template('profile.html', user_data=user_data, editing=False, message=message, edit_error=edit_error)

@app.route('/tamasbama')
def tamasbama():
    return render_template('tamasbama.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
