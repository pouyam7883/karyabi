''' app.py '''
#/user/bin/python

# standard imports
import time
import os

# Framework imports
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

#local imports
import helper
import paths
import config

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')


@app.route(paths.MAIN_ROUTE_APP)
def handle_index():
    '''this route handle main page'''
    return render_template('index.html')


@app.route(paths.AUTH_ROUTE_APP, methods=['GET', 'POST'])
def handle_auth():
    '''this route handle auth of user'''

    if request.method == 'POST':
        data = request.json
        phone = data.get('phone')
        code = data.get('code')


        if code:

            # Code verification
            code_sent_time = session.get('code_time', 0)

            if 'code' in session and code.isdigit():

                if int(code) == session.get('code'):

                    if time.time() - code_sent_time <= 120:

                        conn, user = helper.read_user_with_phone(phone)

                        if conn:

                            if user:
                                conn.close()  # بستن اتصال
                                return jsonify({'success': True, 'redirect': url_for('handle_login')})

                            else:
                                conn.close()  # بستن اتصال
                                return jsonify({'success': True, 'redirect': url_for('handle_register')})

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
            code = helper.generate_random_code()

            if helper.send_verification_code(phone, code):

                session['phone'] = phone
                session['code'] = code
                session['code_time'] = time.time()

                return jsonify({'success': True})

            else:

                return jsonify({'success': False})

    return render_template('auth.html')



@app.route(paths.SEND_CODE_ROUTE, methods=['POST'])
def handle_send_code():
    '''this function handle send sms for user'''

    data = request.get_json()
    phone = data.get('phone')

    if phone:

        code = helper.generate_random_code()
        result = helper.send_verification_code(phone, code)

        if result.get('success'):

            session['reset_code'] = code
            session['reset_code_phone'] = phone
            session['code_time'] = time.time()  # Save the time when code was sent

            return jsonify({'success': True})

    return jsonify({'success': False})


@app.route(paths.RESET_PASS_ROUTE, methods=['GET', 'POST'])
def handle_reset_password():
    '''this function handle reset password for user'''

    if request.method == 'POST':

        data = request.json
        phone = data.get('phone')
        code = data.get('code')
        new_password = data.get('newPassword')
        confirm_password = data.get('confirmPassword')

        if phone and not code:

            # Step 1: Send verification code
            verification_code = str(helper.generate_random_code())
            session['reset_code'] = verification_code
            session['reset_code_phone'] = phone
            session['code_time'] = time.time()

            send_result = helper.send_verification_code(phone, verification_code)

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
            conn, ok = helper.reset_password_user(hashed_password, session['reset_code_phone'])

            if conn and ok:

                session.pop('reset_code', None)
                session.pop('reset_code_phone', None)
                session.pop('code_time', None)

                return jsonify({"success": True, "message": "رمز عبور با موفقیت تغییر کرد."})

            else:

                return jsonify({"success": False, "error": "خطا در اتصال به پایگاه داده."})

    return render_template('reset_password.html')




@app.route(paths.RESEND_RESET_CODE, methods=['POST'])
def handle_resend_reset_code():
    '''this function handle resend reset code'''

    phone = session.get('reset_code_phone')

    if phone:

        verification_code = str(helper.generate_random_code())
        session['reset_code'] = verification_code
        session['code_time'] = time.time()

        send_result = helper.send_verification_code(phone, verification_code)

        if send_result:

            return jsonify({"success": True, "message": "کد تایید مجدداً ارسال شد."})

        else:

            return jsonify({"success": False, "error": "خطا در ارسال مجدد کد تایید."})

    else:

        return jsonify({"success": False, "error": "شماره تلفن در session ذخیره نشده است."})



@app.route(paths.REGISTER_ROUTE, methods=['GET', 'POST'])
def handle_register():
    '''this function handle register user'''

    if request.method == 'POST':

        phone = session.get('phone')
        name = request.form['name']
        lastname = request.form['lastname']
        father_name = request.form['fatherName']
        national_code = request.form['nationalCode']
        email = request.form['email']
        birth_place = request.form['birthPlace']
        birth_date = request.form['birthDate']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']

        if password != confirm_password:

            return "رمز عبور و تکرار آن با هم مطابقت ندارند"

        hashed_password = generate_password_hash(password)  # Hash the password

        conn, ok = helper.register_user(phone, name, lastname, father_name, national_code, email, birth_place, birth_date, hashed_password)

        if conn and ok:

            # success
            conn.close()  # بستن اتصال

            # ذخیره کد ملی و رمز عبور در session
            session['user'] = {
                'national_code': national_code,
                'password': password  # می‌توانید رمز عبور را در session ذخیره کنید
            }

            return redirect(url_for('handle_success'))

        return "خطای پایگاه داده"

    return render_template('register.html')



@app.route(paths.SUCCESS_ROUTE)
def handle_success():
    '''this function handle success page route'''

    user = session.get('user', {})
    user_name = user.get('name', 'کاربر')

    return render_template('success.html', user_name=user_name)

@app.route(paths.LOGIN_ROUTE, methods=['GET', 'POST'])
def handle_login():
    '''this function handle login route'''

    error_message = None
    forgot_password = False

    if request.method == 'POST':

        national_code = request.form['national_code']
        password = request.form['password']

        conn, user = helper.read_user_with_national_code(national_code)

        if conn:

            if user:
                # فرض بر این است که password در ایندکس 8 قرار دارد
                if check_password_hash(user[9], password):  # تغییر ایندکس به 8
                    # فرض بر این است که index 2 نام و index 1 شماره تلفن است
                    session['user'] = {'name': user[2], 'phone': user[1]}
                    conn.close()  # بستن اتصال
                    return redirect(url_for('handle_dashboard'))

                else:
                    error_message = "رمز عبور نادرست است."
                    forgot_password = True

            else:
                error_message = "کد کاربری نادرست است."

        else:
            error_message = "خطای پایگاه داده"

    return render_template('login.html', error_message=error_message, forgot_password=forgot_password)



@app.route(paths.EMPLOYER_ROUTE)
def handle_employer():
    '''this function handle eployer route'''

    return render_template('employer.html')


@app.route(paths.DASHBOARD_ROUTE)
def handle_dashboard():
    '''this functin handle dashboard route'''

    user = session.get('user')

    if user:

        return render_template('dashboard.html', user_name=user.get('name', 'کاربر'))

    return redirect(url_for('handle_login'))

@app.route(paths.SEARCH_JOB_ROUTE)
def handle_search_job():
    '''this function handle search job'''

    return 'صفحه جستجوی شغل'



@app.route(paths.COMPLETION_ROUTE, methods=['GET', 'POST'])
def handle_completion():
    '''this function handle completion'''

    user = session.get('user')

    if not user:

        return redirect(url_for('handle_login'))

    user_data = {}
    has_submitted = False
    success_message = None  # برای نمایش پیام موفقیت

    conn, result = helper.read_user_datas_with_phone(user['phone'])

    if conn:

        if result:

            conn.close()  # بستن اتصال
            user_data = dict(zip(['national_code', 'email', 'name', 'last_name', 'father_name', 'birth_place', 'birth_date'], result))
            has_submitted = True

        else:

            return jsonify({'message': "کاربر یافت نشد."}), 404

    else:

        return jsonify({'message': "خطای پایگاه داده: لطفاً دوباره تلاش کنید."}), 500

    if request.method == 'POST' and has_submitted:

        form_data = request.form.to_dict()

        # اعتبارسنجی داده‌ها
        required_fields = ['national_code', 'email', 'name', 'last_name', 'father_name', 'birth_date', 'birth_place']

        for field in required_fields:

            if field not in form_data or not form_data[field].strip():

                return jsonify({'message': f"فیلد {field} نمی‌تواند خالی باشد."}), 400

        conn, ok = helper.completion_register_user(form_data)

        if conn and ok:

            success_message = "اطلاعات با موفقیت در پایگاه داده ثبت شد."  # پیام موفقیت
            conn.close()  # بستن اتصال

            session['user'] = {'name': form_data['name'], 'phone': form_data["contact_number"]}
            return redirect(url_for('handle_dashboard'))

        else :

            return jsonify({'message': "خطای پایگاه داده: لطفاً دوباره تلاش کنید."}), 500

    site_key = os.environ.get(config.SITE_KEY)
    print("here")

    return render_template('completion.html', user_data=user_data, has_submitted=has_submitted, success_message=success_message, site_key=site_key)


@app.route(paths.PROFILE_ROUTE, methods=['GET', 'POST'])
def handle_profile():
    '''this function handle profile route'''

    user = session.get('user')

    if not user:
        return redirect(url_for('handle_login'))

    user_data = None
    message = None
    edit_error = None

    conn, user_data = helper.read_user_with_phone_from_user(user['phone'])

    if conn:

        if request.method == 'POST':

            if 'edit' in request.form:

                conn.close()
                return render_template('profile.html', user_data=user_data, editing=True)

            elif 'save' in request.form:

                name = request.form['name']
                father_name = request.form['father_name']
                email = request.form['email']
                birth_place = request.form['birth_place']
                birth_date = request.form['birth_date']

                if not all([name, father_name, email, birth_place, birth_date]):

                    edit_error = "لطفاً تمامی فیلدها را پر کنید."
                    return render_template('profile.html', user_data=user_data, editing=True, edit_error=edit_error)

                conn, ok = helper.update_user_datas_with_phone(name, father_name, email, birth_place, birth_date,user['phone'])

                if conn and ok:

                    conn.commit()
                    conn.close()
                    _, user_data = helper.read_user_with_phone_from_user(user['phone'])

                    message = "اطلاعات شما با موفقیت ثبت شد"

                    return render_template('profile.html', user_data=user_data, editing=False, message=message)

                else:

                    edit_error = "خطا در ثبت اطلاعات"
                    return render_template('profile.html', user_data=user_data, editing=True, edit_error=edit_error)

            elif 'cancel' in request.form:
                return redirect(url_for('handle_profile'))

        _, user_data = helper.read_user_with_phone_from_user(user['phone'])

    else:
        edit_error = "خطا در ارتباط با پایگاه داده"

    return render_template('profile.html', user_data=user_data, editing=False, message=message, edit_error=edit_error)

@app.route(paths.CONTACT_US_ROUTE)
def handle_contact_us():
    '''this function handle contact us'''

    return render_template('tamasbama.html')

@app.route(paths.LOGOUT_ROUTE)
def handle_logout():
    '''this function handle logout user'''

    session.pop('user', None)

    return redirect(url_for('handle_login'))

if __name__ == '__main__':

    if config.IS_DEVELOPMENT :

        app.run(port=5000, debug=config.IS_DEVELOPMENT)

    app.run(port=80, debug=config.IS_DEVELOPMENT)
