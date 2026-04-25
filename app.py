from flask import Flask, render_template, request, redirect, url_for, session, make_response, flash
import pymysql
import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

db = None

def get_db():
    global db

    try:
        if db is None:
            raise Exception("No connection")

        db.ping(reconnect=True)

    except:
        db = pymysql.connect(
            host=os.environ.get("DB_HOST"),
            port=int(os.environ.get("DB_PORT", 25060)),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            database=os.environ.get("DB_NAME"),
            ssl={"ca": "ca.pem"}
        )

    return db

@app.before_request
def before_request():
    global db
    db = get_db()

# List of common timezones for the settings dropdown
COMMON_TIMEZONES = [
    ('UTC', 'UTC (Coordinated Universal Time)'),
    ('Africa/Cairo', 'Africa - Cairo (GMT+2)'),
    ('Africa/Johannesburg', 'Africa - Johannesburg (GMT+2)'),
    ('Africa/Lagos', 'Africa - Lagos (GMT+1)'),
    ('America/Anchorage', 'America - Anchorage (GMT-9)'),
    ('America/Argentina/Buenos_Aires', 'America - Buenos Aires (GMT-3)'),
    ('America/Bogota', 'America - Bogota (GMT-5)'),
    ('America/Chicago', 'America - Chicago (GMT-6)'),
    ('America/Denver', 'America - Denver (GMT-7)'),
    ('America/Halifax', 'America - Halifax (GMT-4)'),
    ('America/Lima', 'America - Lima (GMT-5)'),
    ('America/Los_Angeles', 'America - Los Angeles (GMT-8)'),
    ('America/Mexico_City', 'America - Mexico City (GMT-6)'),
    ('America/New_York', 'America - New York (GMT-5)'),
    ('America/Panama', 'America - Panama (GMT-5)'),
    ('America/Phoenix', 'America - Phoenix (GMT-7)'),
    ('America/Santiago', 'America - Santiago (GMT-4)'),
    ('America/Sao_Paulo', 'America - Sao Paulo (GMT-3)'),
    ('America/Toronto', 'America - Toronto (GMT-5)'),
    ('America/Vancouver', 'America - Vancouver (GMT-8)'),
    ('Asia/Baghdad', 'Asia - Baghdad (GMT+3)'),
    ('Asia/Bangkok', 'Asia - Bangkok (GMT+7)'),
    ('Asia/Colombo', 'Asia - Colombo (GMT+5:30)'),
    ('Asia/Dhaka', 'Asia - Dhaka (GMT+6)'),
    ('Asia/Dubai', 'Asia - Dubai (GMT+4)'),
    ('Asia/Ho_Chi_Minh', 'Asia - Ho Chi Minh (GMT+7)'),
    ('Asia/Hong_Kong', 'Asia - Hong Kong (GMT+8)'),
    ('Asia/Jakarta', 'Asia - Jakarta (GMT+7)'),
    ('Asia/Jerusalem', 'Asia - Jerusalem (GMT+2)'),
    ('Asia/Karachi', 'Asia - Karachi (GMT+5)'),
    ('Asia/Kathmandu', 'Asia - Kathmandu (GMT+5:45)'),
    ('Asia/Kolkata', 'Asia - Kolkata (GMT+5:30)'),
    ('Asia/Kuala_Lumpur', 'Asia - Kuala Lumpur (GMT+8)'),
    ('Asia/Manila', 'Asia - Manila (GMT+8)'),
    ('Asia/Seoul', 'Asia - Seoul (GMT+9)'),
    ('Asia/Shanghai', 'Asia - Shanghai (GMT+8)'),
    ('Asia/Singapore', 'Asia - Singapore (GMT+8)'),
    ('Asia/Taipei', 'Asia - Taipei (GMT+8)'),
    ('Asia/Tehran', 'Asia - Tehran (GMT+3:30)'),
    ('Asia/Tokyo', 'Asia - Tokyo (GMT+9)'),
    ('Australia/Brisbane', 'Australia - Brisbane (GMT+10)'),
    ('Australia/Melbourne', 'Australia - Melbourne (GMT+10)'),
    ('Australia/Perth', 'Australia - Perth (GMT+8)'),
    ('Australia/Sydney', 'Australia - Sydney (GMT+10)'),
    ('Europe/Amsterdam', 'Europe - Amsterdam (GMT+1)'),
    ('Europe/Athens', 'Europe - Athens (GMT+2)'),
    ('Europe/Berlin', 'Europe - Berlin (GMT+1)'),
    ('Europe/Brussels', 'Europe - Brussels (GMT+1)'),
    ('Europe/Budapest', 'Europe - Budapest (GMT+1)'),
    ('Europe/Dublin', 'Europe - Dublin (GMT+0)'),
    ('Europe/Helsinki', 'Europe - Helsinki (GMT+2)'),
    ('Europe/Istanbul', 'Europe - Istanbul (GMT+3)'),
    ('Europe/Lisbon', 'Europe - Lisbon (GMT+0)'),
    ('Europe/London', 'Europe - London (GMT+0)'),
    ('Europe/Madrid', 'Europe - Madrid (GMT+1)'),
    ('Europe/Moscow', 'Europe - Moscow (GMT+3)'),
    ('Europe/Oslo', 'Europe - Oslo (GMT+1)'),
    ('Europe/Paris', 'Europe - Paris (GMT+1)'),
    ('Europe/Prague', 'Europe - Prague (GMT+1)'),
    ('Europe/Rome', 'Europe - Rome (GMT+1)'),
    ('Europe/Stockholm', 'Europe - Stockholm (GMT+1)'),
    ('Europe/Vienna', 'Europe - Vienna (GMT+1)'),
    ('Europe/Warsaw', 'Europe - Warsaw (GMT+1)'),
    ('Europe/Zurich', 'Europe - Zurich (GMT+1)'),
    ('Pacific/Auckland', 'Pacific - Auckland (GMT+12)'),
    ('Pacific/Fiji', 'Pacific - Fiji (GMT+12)'),
    ('Pacific/Honolulu', 'Pacific - Honolulu (GMT-10)'),
    ('Pacific/Port_Moresby', 'Pacific - Port Moresby (GMT+10)'),
]

def get_setting(key, default=''):
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT setting_value FROM settings WHERE setting_key=%s", (key,))
    result = cursor.fetchone()
    cursor.close()
    return result['setting_value'] if result else default

def get_timezone():
    """Get the system timezone from settings, default to UTC"""
    tz_name = get_setting('system_timezone', 'UTC')
    try:
        return ZoneInfo(tz_name)
    except Exception:
        return ZoneInfo('UTC')

def get_local_time():
    """Get current time in the system's timezone"""
    return datetime.now(get_timezone())

def get_local_now():
    """Get current local datetime as naive string for display"""
    return datetime.now(get_timezone())

def to_user_timezone(dt):
    """Convert a datetime to user's timezone"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        # Naive datetime, attach UTC then convert
        dt = dt.replace(tzinfo=ZoneInfo('UTC'))
    return dt.astimezone(get_timezone())

def format_local_datetime(dt, format='%Y-%m-%d %H:%M'):
    """Format a datetime in user's timezone"""
    if dt is None:
        return '-'
    local_dt = to_user_timezone(dt)
    return local_dt.strftime(format)

def require_login(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    email = request.form['email']
    password = request.form['password']

    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
    user = cursor.fetchone()
    cursor.close()

    if user:
        session['user'] = user['email']
        session['role'] = user['role']
        return redirect(url_for('dashboard'))
    else:
        return "Invalid credentials. <a href='/login'>Try again</a>"

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
@require_login
def dashboard():
    cursor = db.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT COUNT(*) as total FROM rooms")
    total_rooms = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as total FROM rooms WHERE status = 'available'")
    available_rooms = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as total FROM rooms WHERE status = 'reserved'")
    reserved_rooms = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as total FROM reservations WHERE status = 'confirmed'")
    total_reservations = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as total FROM checkins WHERE status = 'checked-in'")
    active_checkins = cursor.fetchone()['total']

    cursor.execute("SELECT SUM(amount) as total FROM payments WHERE status = 'completed'")
    total_revenue = cursor.fetchone()['total'] or 0

    # Revenue by day (last 7 days)
    cursor.execute("""
        SELECT DATE(created_at) as date, SUM(amount) as total
        FROM payments
        WHERE status = 'completed' AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        GROUP BY DATE(created_at)
        ORDER BY date
    """)
    revenue_data = cursor.fetchall()

    # Room occupancy by type
    cursor.execute("""
        SELECT type, COUNT(*) as count
        FROM rooms
        GROUP BY type
    """)
    room_types = cursor.fetchall()

    # Reservations by status
    cursor.execute("""
        SELECT status, COUNT(*) as count
        FROM reservations
        GROUP BY status
    """)
    reservation_status = cursor.fetchall()

    # Recent payments
    cursor.execute("""
        SELECT p.*, c.guest_name, rom.room_number
        FROM payments p
        JOIN checkins c ON p.checkin_id = c.id
        JOIN rooms rom ON c.room_id = rom.id
        WHERE p.status = 'completed'
        ORDER BY p.created_at DESC
        LIMIT 5
    """)
    recent_payments = cursor.fetchall()

    cursor.close()

    return render_template('dashboard.html', email=session['user'],
                         total_rooms=total_rooms, available_rooms=available_rooms,
                         reserved_rooms=reserved_rooms,
                         total_reservations=total_reservations, active_checkins=active_checkins,
                         total_revenue=total_revenue, revenue_data=revenue_data,
                         room_types=room_types, reservation_status=reservation_status,
                         recent_payments=recent_payments)

# ==================== ROOM MANAGEMENT ====================

@app.route('/rooms')
@require_login
def rooms():
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM rooms ORDER BY room_number")
    rooms_list = cursor.fetchall()
    cursor.close()
    return render_template('rooms.html', rooms=rooms_list)

@app.route('/rooms/add', methods=['POST'])
@require_login
def add_room():
    room_number = request.form['room_number']
    room_type = request.form['type']
    price = request.form['price']

    image_filename = None
    if 'image' in request.files and request.files['image'].filename:
        image_file = request.files['image']
        from werkzeug.utils import secure_filename
        import uuid
        ext = image_file.filename.rsplit('.', 1)[1].lower() if '.' in image_file.filename else 'jpg'
        image_filename = str(uuid.uuid4()) + '.' + ext
        upload_path = os.path.join('static', 'uploads', 'rooms', image_filename)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        image_file.save(upload_path)

    cursor = db.cursor()
    if image_filename:
        cursor.execute("INSERT INTO rooms (room_number, type, price, image) VALUES (%s, %s, %s, %s)",
                      (room_number, room_type, price, image_filename))
    else:
        cursor.execute("INSERT INTO rooms (room_number, type, price) VALUES (%s, %s, %s)",
                      (room_number, room_type, price))
    db.commit()
    cursor.close()
    return redirect(url_for('rooms'))

@app.route('/rooms/<int:id>/edit', methods=['POST'])
@require_login
def edit_room(id):
    room_number = request.form['room_number']
    room_type = request.form['type']
    price = request.form['price']
    status = request.form['status']

    image_filename = None
    if 'image' in request.files and request.files['image'].filename:
        image_file = request.files['image']
        from werkzeug.utils import secure_filename
        import uuid
        ext = image_file.filename.rsplit('.', 1)[1].lower() if '.' in image_file.filename else 'jpg'
        image_filename = str(uuid.uuid4()) + '.' + ext
        upload_path = os.path.join('static', 'uploads', 'rooms', image_filename)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        image_file.save(upload_path)

    cursor = db.cursor()
    if image_filename:
        cursor.execute("UPDATE rooms SET room_number=%s, type=%s, price=%s, status=%s, image=%s WHERE id=%s",
                      (room_number, room_type, price, status, image_filename, id))
    else:
        cursor.execute("UPDATE rooms SET room_number=%s, type=%s, price=%s, status=%s WHERE id=%s",
                      (room_number, room_type, price, status, id))
    db.commit()
    cursor.close()
    return redirect(url_for('rooms'))

@app.route('/rooms/<int:id>/delete', methods=['POST'])
@require_login
def delete_room(id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM rooms WHERE id=%s", (id,))
    db.commit()
    cursor.close()
    return redirect(url_for('rooms'))

# ==================== RESERVATIONS ====================

@app.route('/reservations')
@require_login
def reservations():
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT r.*, rom.room_number, rom.type, rom.price
        FROM reservations r
        JOIN rooms rom ON r.room_id = rom.id
        ORDER BY r.created_at DESC
    """)
    reservations_list = cursor.fetchall()
    cursor.close()

    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM rooms WHERE status = 'available'")
    available_rooms = cursor.fetchall()
    cursor.close()

    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM rooms ORDER BY room_number")
    rooms = cursor.fetchall()
    cursor.close()

    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT c.*, rom.room_number, rom.type
        FROM checkins c
        JOIN rooms rom ON c.room_id = rom.id
        WHERE c.status = 'checked-in'
    """)
    active_checkins = cursor.fetchall()
    cursor.close()

    return render_template('reservations.html', reservations=reservations_list, available_rooms=available_rooms,
                         rooms=rooms, active_checkins=active_checkins)

@app.route('/reservations/add', methods=['POST'])
@require_login
def add_reservation():
    guest_name = request.form['guest_name']
    email = request.form['email']
    phone = request.form['phone']
    room_id = request.form['room_id']
    check_in = request.form['check_in']
    check_out = request.form['check_out']
    downpayment_amount = request.form.get('downpayment_amount', '0')

    # Validate downpayment format
    try:
        downpayment_amount = float(downpayment_amount) if downpayment_amount else 0
        if downpayment_amount < 0:
            return "Error: Downpayment cannot be negative. <a href='/reservations'>Go Back</a>"
    except ValueError:
        return "Error: Invalid downpayment amount. <a href='/reservations'>Go Back</a>"

    # Validate date range - must be within 5 months from today
    today = datetime.now().date()
    max_date = today + timedelta(days=150)  # approximately 5 months

    try:
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return "Invalid date format. Please use YYYY-MM-DD format. <a href='/reservations'>Go Back</a>"

    # Validate dates
    if check_in_date < today:
        return "Check-in date cannot be in the past. <a href='/reservations'>Go Back</a>"

    if check_out_date <= check_in_date:
        return "Check-out date must be after check-in date. <a href='/reservations'>Go Back</a>"

    if check_in_date > max_date or check_out_date > max_date:
        return f"Reservations cannot exceed 5 months from today ({max_date.strftime('%Y-%m-%d')}). Please select shorter dates. <a href='/reservations'>Go Back</a>"

    # Get room price to validate downpayment
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT price FROM rooms WHERE id = %s", (room_id,))
    room = cursor.fetchone()
    if room:
        total_price = float(room['price']) * ((check_out_date - check_in_date).days)
        if downpayment_amount > total_price:
            cursor.close()
            return f"Error: Downpayment cannot exceed total price ({total_price}). <a href='/reservations'>Go Back</a>"
    cursor.close()

    # Only check for CONFIRMED reservations as blockers (pending/cancelled don't block new bookings)
    # OVERLAP DETECTION: Two ranges overlap if: A.start < B.end AND A.end > B.start
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT * FROM reservations
        WHERE room_id = %s AND status = 'confirmed'
        AND check_in < %s AND check_out > %s
    """, (room_id, check_out, check_in))
    overlap = cursor.fetchone()
    cursor.close()

    if overlap:
        return "Room is already booked for selected dates (confirmed reservation exists). <a href='/reservations'>Go Back</a>"

    # Check for active check-ins that would conflict
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT * FROM checkins
        WHERE room_id = %s AND status = 'checked-in'
        AND check_in_time < %s AND (check_out_time IS NULL OR check_out_time > %s)
    """, (room_id, check_out, check_in))
    active_overlap = cursor.fetchone()
    cursor.close()

    if active_overlap:
        return "Room is currently occupied (active check-in exists). Please choose different dates or a different room. <a href='/reservations'>Go Back</a>"

    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO reservations (guest_name, email, phone, room_id, check_in, check_out, status, downpayment_amount)
        VALUES (%s, %s, %s, %s, %s, %s, 'pending', %s)
    """, (guest_name, email, phone, room_id, check_in, check_out, downpayment_amount))
    db.commit()
    cursor.close()
    return redirect(url_for('reservations'))

@app.route('/reservations/<int:id>/confirm', methods=['POST'])
@require_login
def confirm_reservation(id):
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("UPDATE reservations SET status='confirmed' WHERE id=%s", (id,))
    db.commit()

    # Get reservation details
    cursor.execute("""
        SELECT r.*, rom.room_number, rom.type, rom.price
        FROM reservations r
        JOIN rooms rom ON r.room_id = rom.id
        WHERE r.id = %s
    """, (id,))
    reservation = cursor.fetchone()

    # Update room status to reserved when confirmed
    if reservation and reservation['room_id']:
        cursor.execute("UPDATE rooms SET status='reserved' WHERE id=%s", (reservation['room_id'],))
        db.commit()

    # Get all email settings in one query
    cursor.execute("SELECT setting_key, setting_value FROM settings WHERE setting_key LIKE 'email_%'")
    email_settings = {row['setting_key']: row['setting_value'] for row in cursor.fetchall()}

    email_enabled = email_settings.get('email_enabled', 'false') == 'true'
    email_confirmation = email_settings.get('email_confirmation', 'false') == 'true'

    print(f"[CONFIRM] email_enabled: {email_enabled}, email_confirmation: {email_confirmation}")

    if email_enabled and email_confirmation and reservation and reservation['email']:
        company_name = email_settings.get('company_name', 'DNZTech IMS')
        currency_symbol = email_settings.get('currency_symbol', '$')

        check_in = reservation['check_in']
        check_out = reservation['check_out']
        nights = (check_out - check_in).days if check_in and check_out else 1
        total = reservation['price'] * nights if reservation.get('price') else 0

        # Build replacements dict
        replacements = {
            'company_name': company_name,
            'guest_name': reservation['guest_name'],
            'room_number': reservation['room_number'],
            'room_type': reservation['type'],
            'check_in': check_in,
            'check_out': check_out,
            'nights': nights,
            'total': total,
            'currency_symbol': currency_symbol
        }

        # Get custom subject and body, render with placeholders
        custom_subject = render_email_template(email_settings.get('email_confirmation_subject', ''), replacements)
        custom_body = render_email_template(email_settings.get('email_confirmation_body', ''), replacements)
        footer = render_email_template(email_settings.get('email_footer', ''), replacements)

        if custom_subject and custom_body:
            subject = custom_subject
            html_body = custom_body + ('\n' + footer if footer else '')
        else:
            subject = f"Reservation Confirmed - {company_name}"
            html_body = f"""
            <h2>{company_name}</h2>
            <h3>Reservation Confirmed!</h3>
            <p>Dear {reservation['guest_name']},</p>
            <p>Your reservation has been confirmed.</p>
            <p><strong>Room:</strong> {reservation['room_number']} ({reservation['type']})</p>
            <p><strong>Check-in:</strong> {check_in}</p>
            <p><strong>Check-out:</strong> {check_out}</p>
            <p><strong>Nights:</strong> {nights}</p>
            <p><strong>Total:</strong> {total}</p>
            <p>We look forward seeing you!</p>
            """ + (footer if footer else '')

        result = send_email(reservation['email'], subject, html_body)
        print(f"[CONFIRM] Email result: {result}")
    else:
        print(f"[CONFIRM] Skipped - enabled: {email_enabled}, confirm: {email_confirmation}, email: {reservation['email'] if reservation else 'none'}")

    cursor.close()
    return redirect(url_for('reservations'))

@app.route('/reservations/<int:id>/cancel', methods=['POST'])
@require_login
def cancel_reservation(id):
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("UPDATE reservations SET status='cancelled' WHERE id=%s", (id,))
    db.commit()

    cursor.execute("SELECT * FROM reservations WHERE id=%s", (id,))
    reservation = cursor.fetchone()

    # Update room status to available when reservation is cancelled
    if reservation and reservation['room_id']:
        cursor.execute("UPDATE rooms SET status='available' WHERE id=%s", (reservation['room_id'],))
        db.commit()

    # Get all email settings in one query
    cursor.execute("SELECT setting_key, setting_value FROM settings WHERE setting_key LIKE 'email_%'")
    email_settings = {row['setting_key']: row['setting_value'] for row in cursor.fetchall()}

    email_enabled = email_settings.get('email_enabled', 'false') == 'true'
    email_cancellation = email_settings.get('email_cancellation', 'false') == 'true'

    print(f"[CANCEL] email_enabled: {email_enabled}, email_cancellation: {email_cancellation}")

    if email_enabled and email_cancellation and reservation and reservation['email']:
        company_name = email_settings.get('company_name', 'DNZTech IMS')

        replacements = {
            'company_name': company_name,
            'guest_name': reservation['guest_name'],
            'check_in': reservation['check_in'],
            'check_out': reservation['check_out']
        }

        custom_subject = render_email_template(email_settings.get('email_cancellation_subject', ''), replacements)
        custom_body = render_email_template(email_settings.get('email_cancellation_body', ''), replacements)
        footer = render_email_template(email_settings.get('email_footer', ''), replacements)

        if custom_subject and custom_body:
            subject = custom_subject
            html_body = custom_body + ('\n' + footer if footer else '')
        else:
            subject = f"Reservation Cancelled - {company_name}"
            html_body = f"""
            <h2>{company_name}</h2>
            <h3>Reservation Cancelled</h3>
            <p>Dear {reservation['guest_name']},</p>
            <p>Your reservation has been cancelled as requested.</p>
            <p><strong>Check-in:</strong> {reservation['check_in']}</p>
            <p><strong>Check-out:</strong> {reservation['check_out']}</p>
            <p>If you have any questions, please contact us.</p>
            """ + (footer if footer else '')

        result = send_email(reservation['email'], subject, html_body)
        print(f"[CANCEL] Email result: {result}")
    else:
        print(f"[CANCEL] Skipped - enabled: {email_enabled}, cancel: {email_cancellation}, email: {reservation['email'] if reservation else 'none'}")

    cursor.close()
    return redirect(url_for('reservations'))

@app.route('/reservations/<int:id>/delete', methods=['POST'])
@require_login
def delete_reservation(id):
    cursor = db.cursor()
    # Set reservation_id to NULL in checkins first (handles foreign key)
    cursor.execute("UPDATE checkins SET reservation_id=NULL WHERE reservation_id=%s", (id,))
    db.commit()
    # Now delete the reservation
    cursor.execute("DELETE FROM reservations WHERE id=%s", (id,))
    db.commit()
    cursor.close()
    return redirect(url_for('reservations'))

# ==================== CHECK-IN / CHECK-OUT ====================

@app.route('/checkins')
@require_login
def checkins():
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT c.*, rom.room_number, rom.type
        FROM checkins c
        JOIN rooms rom ON c.room_id = rom.id
        ORDER BY c.check_in_time DESC
    """)
    checkins_list = cursor.fetchall()
    cursor.close()

    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT r.*, rom.room_number, rom.price, rom.type
        FROM reservations r
        JOIN rooms rom ON r.room_id = rom.id
        WHERE r.status = 'confirmed' AND r.id NOT IN (
            SELECT reservation_id FROM checkins WHERE reservation_id IS NOT NULL
        )
    """)
    confirmed_reservations = cursor.fetchall()
    cursor.close()

    return render_template('checkins.html', checkins=checkins_list, confirmed_reservations=confirmed_reservations)

@app.route('/api/reservation/<int:id>/payment-summary')
@require_login
def get_reservation_payment_summary(id):
    """Return payment summary for a reservation"""
    cursor = db.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT r.*, rom.price as room_rate, rom.room_number
        FROM reservations r
        JOIN rooms rom ON r.room_id = rom.id
        WHERE r.id = %s
    """, (id,))
    reservation = cursor.fetchone()

    if not reservation:
        cursor.close()
        return {'error': 'Reservation not found'}, 404

    check_in = reservation['check_in']
    check_out = reservation['check_out']
    nights = (check_out - check_in).days if check_in and check_out else 1
    room_rate = float(reservation['room_rate'])
    total_price = room_rate * nights
    downpayment_amount = float(reservation.get('downpayment_amount') or 0)
    remaining_balance = total_price - downpayment_amount

    if downpayment_amount == 0:
        payment_status = 'unpaid'
        status_class = 'secondary'
    elif remaining_balance == 0:
        payment_status = 'fully_paid'
        status_class = 'success'
    else:
        payment_status = 'partial'
        status_class = 'warning'

    cursor.close()

    return {
        'room_rate': room_rate,
        'nights': nights,
        'total_price': total_price,
        'downpayment_amount': downpayment_amount,
        'remaining_balance': remaining_balance,
        'payment_status': payment_status,
        'status_class': status_class
    }

@app.route('/checkins/add', methods=['POST'])
@require_login
def add_checkin():
    reservation_id = request.form.get('reservation_id')
    room_id = request.form['room_id']
    guest_name = request.form['guest_name']

    # Validate foreign key relationships FIRST
    cursor = db.cursor(pymysql.cursors.DictCursor)

    # Verify room exists
    cursor.execute("SELECT id, status FROM rooms WHERE id = %s", (room_id,))
    room = cursor.fetchone()
    if not room:
        cursor.close()
        return "Error: Room does not exist. <a href='/checkins'>Go Back</a>"

    # If reservation_id provided, verify it exists and validate dates
    if reservation_id:
        cursor.execute("""
            SELECT id, room_id, check_in, check_out, status
            FROM reservations WHERE id = %s
        """, (reservation_id,))
        reservation = cursor.fetchone()

        if not reservation:
            cursor.close()
            return "Error: Reservation does not exist. <a href='/checkins'>Go Back</a>"

        # SECURITY: Verify room matches reservation
        if str(reservation['room_id']) != str(room_id):
            cursor.close()
            return "Error: Selected room does not match reservation room. <a href='/checkins'>Go Back</a>"

        # SECURITY: Verify reservation is confirmed (not pending/cancelled)
        if reservation['status'] != 'confirmed':
            cursor.close()
            return "Error: Reservation is not confirmed. <a href='/checkins'>Go Back</a>"

        # SECURITY: Enforce no early check-in
        # Check-in is ONLY allowed when current_date >= check_in_date
        today = datetime.now().date()
        reservation_check_in = reservation['check_in']

        if isinstance(reservation_check_in, datetime):
            reservation_check_in = reservation_check_in.date()

        if today < reservation_check_in:
            cursor.close()
            days_early = (reservation_check_in - today).days
            return f"Error: Cannot check in early. Reservation starts on {reservation['check_in']} ({days_early} days from now). <a href='/checkins'>Go Back</a>"

        # Verify no active check-in already exists for this reservation
        cursor.execute("""
            SELECT id FROM checkins
            WHERE reservation_id = %s AND status = 'checked-in'
        """, (reservation_id,))
        existing = cursor.fetchone()
        if existing:
            cursor.close()
            return "Error: This reservation already has an active check-in. <a href='/checkins'>Go Back</a>"

    # Calculate pricing for reservation-based check-ins
    total_price = 0
    downpayment_amount = 0
    remaining_balance = 0
    payment_status = 'unpaid'

    if reservation_id:
        # Get room price and calculate total
        cursor.execute("SELECT price FROM rooms WHERE id = %s", (room_id,))
        room_price = cursor.fetchone()['price']

        check_in_date = reservation['check_in']
        check_out_date = reservation['check_out']
        number_of_nights = (check_out_date - check_in_date).days

        total_price = float(room_price) * number_of_nights

        # Get downpayment from reservation if exists
        cursor.execute("SELECT downpayment_amount FROM reservations WHERE id = %s", (reservation_id,))
        res = cursor.fetchone()
        downpayment_amount = float(res['downpayment_amount']) if res and res['downpayment_amount'] else 0

        # Validate downpayment doesn't exceed total
        if downpayment_amount > total_price:
            cursor.close()
            return "Error: Downpayment cannot exceed total price. <a href='/checkins'>Go Back</a>"

        remaining_balance = total_price - downpayment_amount

        # Determine payment status
        if downpayment_amount == 0:
            payment_status = 'unpaid'
        elif remaining_balance == 0:
            payment_status = 'fully_paid'
        else:
            payment_status = 'partial'

        print(f"[CHECKIN PRICING] Total: {total_price}, Downpayment: {downpayment_amount}, Remaining: {remaining_balance}, Status: {payment_status}")

    cursor.close()

    # NOW perform the check-in (all validations passed)
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO checkins (reservation_id, room_id, guest_name, check_in_time, status,
                              total_price, downpayment_amount, remaining_balance, payment_status)
        VALUES (%s, %s, %s, %s, 'checked-in', %s, %s, %s, %s)
    """, (reservation_id if reservation_id else None, room_id, guest_name, datetime.now(),
          total_price, downpayment_amount, remaining_balance, payment_status))
    db.commit()

    if reservation_id:
        cursor.execute("UPDATE reservations SET status='confirmed' WHERE id=%s", (reservation_id,))
        db.commit()

    cursor.execute("UPDATE rooms SET status='occupied' WHERE id=%s", (room_id,))
    db.commit()
    cursor.close()

    print(f"[CHECKIN] Guest '{guest_name}' checked into room {room_id}")
    if reservation_id:
        print(f"[CHECKIN] Linked to reservation {reservation_id}")

    return redirect(url_for('checkins'))

@app.route('/checkins/<int:id>/checkout', methods=['GET'])
@require_login
def checkout(id):
    """Redirect to checkout summary"""
    return redirect(url_for('checkout_summary', id=id))

@app.route('/checkout-summary/<int:id>')
@require_login
def checkout_summary(id):
    """Generate checkout summary with room cost + food orders"""
    # SECURITY: Always use global tax rate from settings - never from user input
    tax_rate = get_tax_rate()

    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT c.*, rom.room_number, rom.type, rom.price as room_price,
               r.guest_name as res_guest_name, r.email as res_email,
               r.check_in as res_check_in, r.check_out as res_check_out
        FROM checkins c
        JOIN rooms rom ON c.room_id = rom.id
        LEFT JOIN reservations r ON c.reservation_id = r.id
        WHERE c.id = %s
    """, (id,))
    checkin = cursor.fetchone()

    if not checkin:
        cursor.close()
        return "Check-in not found"

    # Calculate nights from reservation dates if available, otherwise from checkin time
    if checkin.get('res_check_in') and checkin.get('res_check_out'):
        check_in_date = checkin['res_check_in']
        check_out_date = checkin['res_check_out']
        nights = (check_out_date - check_in_date).days
    else:
        check_in_time = checkin['check_in_time']
        check_out_time = datetime.now()
        nights = (check_out_time - check_in_time).days

    # Ensure minimum 1 night, no zero/negative
    nights = max(1, nights)

    print(f"[CHECKOUT SUMMARY] Checkin ID: {id}")
    print(f"[CHECKOUT SUMMARY] Guest: {checkin['guest_name']}, Room: {checkin['room_number']}")
    print(f"[CHECKOUT SUMMARY] Nights: {nights}, Room price: {checkin['room_price']}")
    if checkin.get('res_check_in') and checkin.get('res_check_out'):
        print(f"[CHECKOUT SUMMARY] Using reservation dates: {checkin['res_check_in']} to {checkin['res_check_out']}")
    else:
        print(f"[CHECKOUT SUMMARY] Using checkin time: {checkin['check_in_time']}")

    room_total = nights * float(checkin['room_price'])
    print(f"[CHECKOUT SUMMARY] Room total: {room_total}")

    # Get food orders total
    cursor.execute("""
        SELECT COALESCE(SUM(quantity * price), 0) as food_total
        FROM food_orders WHERE checkin_id = %s
    """, (id,))
    food_total = float(cursor.fetchone()['food_total'])

    cursor.execute("""
        SELECT * FROM food_orders WHERE checkin_id = %s ORDER BY order_time
    """, (id,))
    food_orders = cursor.fetchall()

    # Get addon orders total
    cursor.execute("""
        SELECT COALESCE(SUM(quantity * price), 0) as addon_total
        FROM addon_orders WHERE checkin_id = %s
    """, (id,))
    addon_total = float(cursor.fetchone()['addon_total'])

    cursor.execute("""
        SELECT ao.*, a.name as addon_name
        FROM addon_orders ao
        JOIN addons a ON ao.addon_id = a.id
        WHERE ao.checkin_id = %s ORDER BY ao.order_time
    """, (id,))
    addon_orders = cursor.fetchall()
    cursor.close()

    grand_total = room_total + food_total + addon_total
    tax = grand_total * (tax_rate / 100)
    final_total = grand_total + tax

    print(f"[CHECKOUT SUMMARY] Food total: {food_total}, Addon total: {addon_total}")
    print(f"[CHECKOUT SUMMARY] Grand total: {grand_total}, Tax: {tax}, Final: {final_total}")

    return render_template('checkout_summary.html',
                         checkin=checkin, food_orders=food_orders,
                         addon_orders=addon_orders,
                         nights=nights, room_total=room_total,
                         food_total=food_total, addon_total=addon_total,
                         grand_total=grand_total,
                         tax=tax, final_total=final_total, tax_rate=tax_rate)

@app.route('/checkouts/create-payment/<int:id>', methods=['POST'])
@require_login
def create_payment_at_checkout(id):
    """Create payment during checkout process - backend calculates total, user cannot manipulate"""
    # SECURITY: Use ONLY global tax rate from settings - never trust user input
    tax_rate = get_tax_rate()

    cursor = db.cursor(pymysql.cursors.DictCursor)

    # Get checkin with full relational data
    cursor.execute("""
        SELECT c.*, rom.room_number, rom.type, rom.price as room_price,
               r.guest_name as res_guest_name, r.email as res_email,
               r.check_in as res_check_in, r.check_out as res_check_out
        FROM checkins c
        JOIN rooms rom ON c.room_id = rom.id
        LEFT JOIN reservations r ON c.reservation_id = r.id
        WHERE c.id = %s
    """, (id,))
    checkin = cursor.fetchone()

    if not checkin:
        cursor.close()
        flash('Check-in not found', 'danger')
        return redirect(url_for('checkins'))

    print(f"[CHECKOUT PAYMENT] Tax rate from settings: {tax_rate}%")

    # Calculate nights from reservation dates if available, otherwise from checkin time
    if checkin.get('res_check_in') and checkin.get('res_check_out'):
        check_in_date = checkin['res_check_in']
        check_out_date = checkin['res_check_out']
        nights = (check_out_date - check_in_date).days
    else:
        check_in_time = checkin['check_in_time']
        check_out_time = datetime.now()
        nights = (check_out_time - check_in_time).days

    # Ensure minimum 1 night - SECURITY: no negative or zero
    nights = max(1, nights)

    # SECURITY: Backend calculates total - never from user input
    room_price = float(checkin['room_price'])
    room_total = nights * room_price

    print(f"[CHECKOUT PAYMENT] nights={nights}, price={room_price}, room_total={room_total}")

    # Get food orders total
    cursor.execute("""
        SELECT COALESCE(SUM(quantity * price), 0) as food_total
        FROM food_orders WHERE checkin_id = %s
    """, (id,))
    food_total = float(cursor.fetchone()['food_total'])

    # Get addon orders total
    cursor.execute("""
        SELECT COALESCE(SUM(quantity * price), 0) as addon_total
        FROM addon_orders WHERE checkin_id = %s
    """, (id,))
    addon_total = float(cursor.fetchone()['addon_total'])

    # Calculate grand total with SECURE tax rate
    subtotal = room_total + food_total + addon_total
    tax = subtotal * (tax_rate / 100)
    final_total = subtotal + tax

    print(f"[CHECKOUT PAYMENT] food={food_total}, addon={addon_total}, subtotal={subtotal}")
    print(f"[CHECKOUT PAYMENT] FINAL CALCULATED TOTAL: {final_total} (tax_rate={tax_rate}%)")

    # Get payment type from form (this is safe to take from user)
    payment_type = request.form.get('payment_type', 'cash')

    # Insert payment with CALCULATED amount - user cannot manipulate
    cursor.execute("""
        INSERT INTO payments (checkin_id, amount, payment_type, status)
        VALUES (%s, %s, %s, 'pending')
    """, (id, final_total, payment_type))
    db.commit()
    payment_id = cursor.lastrowid

    # Update checkin status to checked-out
    cursor.execute("""
        UPDATE checkins SET check_out_time=%s, status='checked-out' WHERE id=%s
    """, (datetime.now(), id))
    db.commit()

    # Update room status to available
    print(f"[CHECKOUT] Step 1: Updating room status")
    if checkin.get('room_id'):
        cursor.execute("UPDATE rooms SET status='available' WHERE id=%s", (checkin['room_id'],))
        db.commit()
        print(f"[CHECKOUT] Room {checkin['room_id']} status set to 'available'")
    else:
        print(f"[CHECKOUT] WARNING: No room_id in checkin record")

    # Delete reservation if linked (checkout complete)
    print(f"[CHECKOUT] Step 2: Deleting reservation")
    if checkin.get('reservation_id'):
        # Clear foreign key in checkins first
        cursor.execute("UPDATE checkins SET reservation_id=NULL WHERE reservation_id=%s", (checkin['reservation_id'],))
        db.commit()
        cursor.execute("DELETE FROM reservations WHERE id=%s", (checkin['reservation_id'],))
        db.commit()
        print(f"[CHECKOUT] Reservation {checkin['reservation_id']} deleted")
    else:
        print(f"[CHECKOUT] WARNING: No reservation_id in checkin record")

    # Update checkin status to checked-out
    print(f"[CHECKOUT] Step 3: Updating checkin status")

    cursor.close()
    print(f"[CHECKOUT] All updates complete for checkin ID: {id}")
    print(f"[CHECKOUT] Redirecting to receipt: {payment_id}")

    return redirect(url_for('print_receipt', id=payment_id))

@app.route('/payments/add', methods=['POST'])
@require_login
def add_payment():
    checkin_id = request.form['checkin_id']
    payment_type = request.form['payment_type']

    # SECURITY: Always use global tax rate from settings - user cannot manipulate
    tax_rate = get_tax_rate()

    cursor = db.cursor(pymysql.cursors.DictCursor)

    # Get checkin with full relational data
    cursor.execute("""
        SELECT c.*, rom.room_number, rom.type, rom.price as room_price,
               r.guest_name as res_guest_name, r.email as res_email,
               r.check_in as res_check_in, r.check_out as res_check_out
        FROM checkins c
        JOIN rooms rom ON c.room_id = rom.id
        LEFT JOIN reservations r ON c.reservation_id = r.id
        WHERE c.id = %s
    """, (checkin_id,))
    checkin = cursor.fetchone()

    if not checkin:
        cursor.close()
        flash('Check-in not found', 'danger')
        return redirect(url_for('payments'))

    # Verify checkin is still active (not already checked out)
    if checkin.get('status') == 'checked-out':
        cursor.close()
        flash('This check-in has already been completed', 'warning')
        return redirect(url_for('payments'))

    print(f"[ADD PAYMENT] Tax rate from settings: {tax_rate}%")
    print(f"[ADD PAYMENT] Guest: {checkin['guest_name']}, Room: {checkin['room_number']}")

    # Calculate nights from reservation dates if available, otherwise from checkin time
    if checkin.get('res_check_in') and checkin.get('res_check_out'):
        check_in_date = checkin['res_check_in']
        check_out_date = checkin['res_check_out']
        nights = (check_out_date - check_in_date).days
        print(f"[ADD PAYMENT] Using reservation dates: nights = {nights}")
    else:
        check_in_time = checkin['check_in_time']
        check_out_time = datetime.now()
        nights = (check_out_time - check_in_time).days
        print(f"[ADD PAYMENT] Using checkin time: nights = {nights}")

    # Ensure minimum 1 night - SECURITY: no negative or zero
    nights = max(1, nights)
    print(f"[ADD PAYMENT] Final nights: {nights}")

    # SECURITY: Backend calculates total - never from user input
    room_price = float(checkin['room_price'])
    room_total = nights * room_price
    print(f"[ADD PAYMENT] Room total: {room_total}")

    # Get food orders total
    cursor.execute("""
        SELECT COALESCE(SUM(quantity * price), 0) as food_total
        FROM food_orders WHERE checkin_id = %s
    """, (checkin_id,))
    food_total = float(cursor.fetchone()['food_total'])

    # Get addon orders total
    cursor.execute("""
        SELECT COALESCE(SUM(quantity * price), 0) as addon_total
        FROM addon_orders WHERE checkin_id = %s
    """, (checkin_id,))
    addon_total = float(cursor.fetchone()['addon_total'])

    # Calculate grand total with SECURE tax rate
    subtotal = room_total + food_total + addon_total
    tax = subtotal * (tax_rate / 100)
    final_total = subtotal + tax

    print(f"[ADD PAYMENT] Food: {food_total}, Addon: {addon_total}")
    print(f"[ADD PAYMENT] FINAL CALCULATED TOTAL: {final_total} (tax_rate={tax_rate}%)")

    # Insert payment with CALCULATED amount - user cannot manipulate
    cursor.execute("""
        INSERT INTO payments (checkin_id, amount, payment_type, status)
        VALUES (%s, %s, %s, 'completed')
    """, (checkin_id, final_total, payment_type))
    db.commit()
    payment_id = cursor.lastrowid

    # Auto-complete: update checkin status, room status, and delete reservation
    # (checkin dict is already available from earlier in this function)
    room_id = checkin.get('room_id')
    reservation_id = checkin.get('reservation_id')

    # Update room status to available
    if room_id:
        cursor.execute("UPDATE rooms SET status='available' WHERE id=%s", (room_id,))
        db.commit()

    # Update checkin status to checked-out
    cursor.execute("UPDATE checkins SET status='checked-out' WHERE id=%s", (checkin_id,))
    db.commit()

    # Delete reservation if linked
    if reservation_id:
        cursor.execute("UPDATE checkins SET reservation_id=NULL WHERE reservation_id=%s", (reservation_id,))
        db.commit()
        cursor.execute("DELETE FROM reservations WHERE id=%s", (reservation_id,))
        db.commit()

    cursor.close()

    print(f"[ADD PAYMENT] Payment created with ID: {payment_id} (auto-completed)")

    return redirect(url_for('print_receipt', id=payment_id))

@app.route('/print-receipt/<int:id>')
@require_login
def print_receipt(id):
    """Generate printable receipt"""
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT p.*, c.guest_name, c.check_in_time, c.check_out_time,
               rom.room_number, rom.type as room_type, rom.price as room_price,
               r.guest_name as res_guest_name, r.check_in as res_check_in,
               r.check_out as res_check_out
        FROM payments p
        JOIN checkins c ON p.checkin_id = c.id
        JOIN rooms rom ON c.room_id = rom.id
        LEFT JOIN reservations r ON c.reservation_id = r.id
        WHERE p.id = %s
    """, (id,))
    payment = cursor.fetchone()

    if not payment:
        cursor.close()
        print(f"[PRINT RECEIPT] Payment ID {id} not found")
        return "Payment not found"

    print(f"[PRINT RECEIPT] Payment ID: {id}")
    print(f"[PRINT RECEIPT] Guest: {payment['guest_name']}, Room: {payment['room_number']}")
    print(f"[PRINT RECEIPT] Amount: {payment['amount']}, Status: {payment['status']}")
    print(f"[PRINT RECEIPT] Reservation check_in: {payment.get('res_check_in')}, check_out: {payment.get('res_check_out')}")

    # Get food orders for this check-in
    cursor.execute("""
        SELECT * FROM food_orders WHERE checkin_id = %s ORDER BY order_time
    """, (payment['checkin_id'],))
    food_orders = cursor.fetchall()

    # Get addon orders for this check-in
    cursor.execute("""
        SELECT ao.*, a.name as addon_name
        FROM addon_orders ao
        JOIN addons a ON ao.addon_id = a.id
        WHERE ao.checkin_id = %s ORDER BY ao.order_time
    """, (payment['checkin_id'],))
    addon_orders = cursor.fetchall()

    cursor.close()

    print(f"[PRINT RECEIPT] Food orders: {len(food_orders)}, Addon orders: {len(addon_orders)}")

    return render_template('receipt.html', payment=payment, food_orders=food_orders, addon_orders=addon_orders)

# ==================== FOODS MANAGEMENT ====================

@app.route('/foods')
@require_login
def foods():
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM foods ORDER BY category, name")
    foods_list = cursor.fetchall()
    cursor.close()
    return render_template('foods.html', foods=foods_list)

@app.route('/foods/add', methods=['POST'])
@require_login
def add_food():
    name = request.form['name']
    price = request.form['price']
    category = request.form['category']

    # Handle image upload
    image_filename = None
    if 'image' in request.files and request.files['image'].filename:
        image_file = request.files['image']
        # Generate unique filename
        from werkzeug.utils import secure_filename
        import uuid
        ext = image_file.filename.rsplit('.', 1)[1].lower() if '.' in image_file.filename else 'jpg'
        image_filename = str(uuid.uuid4()) + '.' + ext
        upload_path = os.path.join('static', 'uploads', 'foods', image_filename)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        image_file.save(upload_path)

    cursor = db.cursor()
    if image_filename:
        cursor.execute("INSERT INTO foods (name, price, category, image) VALUES (%s, %s, %s, %s)",
                      (name, price, category, image_filename))
    else:
        cursor.execute("INSERT INTO foods (name, price, category) VALUES (%s, %s, %s)",
                      (name, price, category))
    db.commit()
    cursor.close()
    return redirect(url_for('foods'))

@app.route('/foods/<int:id>/edit', methods=['POST'])
@require_login
def edit_food(id):
    name = request.form['name']
    price = request.form['price']
    category = request.form['category']
    available = 'available' in request.form

    # Handle image upload
    image_filename = None
    if 'image' in request.files and request.files['image'].filename:
        image_file = request.files['image']
        from werkzeug.utils import secure_filename
        import uuid
        ext = image_file.filename.rsplit('.', 1)[1].lower() if '.' in image_file.filename else 'jpg'
        image_filename = str(uuid.uuid4()) + '.' + ext
        upload_path = os.path.join('static', 'uploads', 'foods', image_filename)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        image_file.save(upload_path)

    cursor = db.cursor()
    if image_filename:
        cursor.execute("UPDATE foods SET name=%s, price=%s, category=%s, available=%s, image=%s WHERE id=%s",
                      (name, price, category, available, image_filename, id))
    else:
        cursor.execute("UPDATE foods SET name=%s, price=%s, category=%s, available=%s WHERE id=%s",
                      (name, price, category, available, id))
    db.commit()
    cursor.close()
    return redirect(url_for('foods'))

@app.route('/foods/<int:id>/delete', methods=['POST'])
@require_login
def delete_food(id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM foods WHERE id=%s", (id,))
    db.commit()
    cursor.close()
    return redirect(url_for('foods'))

@app.route('/foods/<int:id>/toggle', methods=['POST'])
@require_login
def toggle_food(id):
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT available FROM foods WHERE id=%s", (id,))
    food = cursor.fetchone()
    cursor.close()

    new_status = not food['available']
    cursor = db.cursor()
    cursor.execute("UPDATE foods SET available=%s WHERE id=%s", (new_status, id))
    db.commit()
    cursor.close()
    return redirect(url_for('foods'))

# ==================== FOOD ORDERS ====================

@app.route('/food-orders')
@require_login
def food_orders():
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT fo.*, c.guest_name, rom.room_number
        FROM food_orders fo
        JOIN checkins c ON fo.checkin_id = c.id
        JOIN rooms rom ON c.room_id = rom.id
        ORDER BY fo.order_time DESC
    """)
    orders = cursor.fetchall()
    cursor.close()

    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT c.*, rom.room_number FROM checkins c JOIN rooms rom ON c.room_id = rom.id WHERE c.status='checked-in'")
    active_checkins = cursor.fetchall()
    cursor.close()

    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM foods ORDER BY category, name")
    foods = cursor.fetchall()
    cursor.close()

    return render_template('food_orders.html', orders=orders, active_checkins=active_checkins, foods=foods)

@app.route('/food-orders/add', methods=['POST'])
@require_login
def add_food_order():
    checkin_id = request.form['checkin_id']
    payment_type = request.form.get('payment_type', 'cash')

    # Handle JSON order items from POS
    if 'order_items_json' in request.form:
        import json
        order_items = json.loads(request.form.get('order_items_json', '[]'))
        cursor = db.cursor()
        for item in order_items:
            cursor.execute("""
                INSERT INTO food_orders (checkin_id, item_name, quantity, price, status)
                VALUES (%s, %s, %s, %s, 'pending')
            """, (checkin_id, item.get('name'), item.get('quantity'), item.get('price')))
        db.commit()
        cursor.close()
        from flask import jsonify
        return jsonify({'success': True, 'message': 'Order placed successfully'})

    # Handle multiple items from POS (format: id:name:qty:price)
    if 'order_items' in request.form:
        order_items = request.form.getlist('order_items')
        cursor = db.cursor()
        for item in order_items:
            parts = item.split(':')
            if len(parts) >= 4:
                _, item_name, quantity, price = parts
                cursor.execute("""
                    INSERT INTO food_orders (checkin_id, item_name, quantity, price)
                    VALUES (%s, %s, %s, %s)
                """, (checkin_id, item_name, quantity, price))
        db.commit()
        cursor.close()
        from flask import jsonify
        return jsonify({'success': True, 'message': 'Order placed successfully'})

    # Handle single item (legacy form submission)
    item_name = request.form['item_name']
    quantity = request.form['quantity']
    price = request.form['price']

    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO food_orders (checkin_id, item_name, quantity, price)
        VALUES (%s, %s, %s, %s)
    """, (checkin_id, item_name, quantity, price))
    db.commit()
    cursor.close()
    return redirect(url_for('food_orders'))

@app.route('/food-orders/<int:id>/update', methods=['POST'])
@require_login
def update_food_order(id):
    status = request.form['status']
    cursor = db.cursor()
    cursor.execute("UPDATE food_orders SET status=%s WHERE id=%s", (status, id))
    db.commit()
    cursor.close()
    return redirect(url_for('food_orders'))

# ==================== ADDON ORDERS ====================

@app.route('/addon-orders')
@require_login
def addon_orders():
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT ao.*, c.guest_name, rom.room_number, a.name as addon_name
        FROM addon_orders ao
        JOIN checkins c ON ao.checkin_id = c.id
        JOIN rooms rom ON c.room_id = rom.id
        JOIN addons a ON ao.addon_id = a.id
        ORDER BY ao.order_time DESC
    """)
    orders = cursor.fetchall()
    cursor.close()

    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT c.*, rom.room_number FROM checkins c JOIN rooms rom ON c.room_id = rom.id WHERE c.status='checked-in'")
    active_checkins = cursor.fetchall()
    cursor.close()

    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM addons WHERE available = TRUE ORDER BY name")
    addons = cursor.fetchall()
    cursor.close()

    return render_template('addon_orders.html', orders=orders, active_checkins=active_checkins, addons=addons)

@app.route('/addon-orders/add', methods=['POST'])
@require_login
def add_addon_order():
    checkin_id = request.form['checkin_id']
    addon_id = request.form['addon_id']
    quantity = request.form.get('quantity', 1)

    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT price FROM addons WHERE id = %s", (addon_id,))
    addon = cursor.fetchone()
    cursor.close()

    if addon:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO addon_orders (checkin_id, addon_id, quantity, price)
            VALUES (%s, %s, %s, %s)
        """, (checkin_id, addon_id, quantity, addon['price']))
        db.commit()
        cursor.close()

    return redirect(url_for('addon_orders'))

@app.route('/addon-orders/<int:id>/update', methods=['POST'])
@require_login
def update_addon_order(id):
    status = request.form['status']
    quantity = request.form.get('quantity')
    price = request.form.get('price')
    cursor = db.cursor()
    if quantity and price:
        cursor.execute("UPDATE addon_orders SET status=%s, quantity=%s, price=%s WHERE id=%s",
                       (status, quantity, price, id))
    else:
        cursor.execute("UPDATE addon_orders SET status=%s WHERE id=%s", (status, id))
    db.commit()
    cursor.close()
    return redirect(url_for('addon_orders'))

@app.route('/addon-orders/<int:id>/edit', methods=['GET'])
@require_login
def edit_addon_order(id):
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM addon_orders WHERE id=%s", (id,))
    order = cursor.fetchone()
    cursor.close()
    return render_template('edit_addon_order.html', order=order)

@app.route('/addon-orders/<int:id>/delete', methods=['POST'])
@require_login
def delete_addon_order(id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM addon_orders WHERE id=%s", (id,))
    db.commit()
    cursor.close()
    return redirect(url_for('addon_orders'))

# ==================== PAYMENTS ====================

@app.route('/payments')
@require_login
def payments():
    cursor = db.cursor(pymysql.cursors.DictCursor)

    # Fetch payments with full relational data
    cursor.execute("""
        SELECT p.*, c.guest_name, rom.room_number, rom.type as room_type,
               r.check_in as res_check_in, r.check_out as res_check_out
        FROM payments p
        JOIN checkins c ON p.checkin_id = c.id
        JOIN rooms rom ON c.room_id = rom.id
        LEFT JOIN reservations r ON c.reservation_id = r.id
        ORDER BY p.created_at DESC
    """)
    payments_list = cursor.fetchall()

    print(f"[PAYMENTS] Loaded {len(payments_list)} payments")
    for p in payments_list:
        print(f"[PAYMENTS] Payment {p['id']}: Guest={p['guest_name']}, Room={p['room_number']}, Amount={p['amount']}")

    cursor.close()

    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT c.*, rom.room_number, rom.price as room_price FROM checkins c JOIN rooms rom ON c.room_id = rom.id WHERE c.status='checked-in'")
    active_checkins = cursor.fetchall()
    cursor.close()

    return render_template('payments.html', payments=payments_list, active_checkins=active_checkins)

@app.route('/payments/<int:id>/complete', methods=['POST'])
@require_login
def complete_payment(id):
    cursor = db.cursor(pymysql.cursors.DictCursor)

    # Get payment and checkin details
    cursor.execute("""
        SELECT p.*, c.id as checkin_id, c.reservation_id, c.room_id, rom.room_number
        FROM payments p
        JOIN checkins c ON p.checkin_id = c.id
        JOIN rooms rom ON c.room_id = rom.id
        WHERE p.id = %s
    """, (id,))
    payment = cursor.fetchone()

    if not payment:
        cursor.close()
        flash('Payment not found', 'danger')
        return redirect(url_for('payments'))

    # Update payment status to completed
    cursor.execute("UPDATE payments SET status='completed' WHERE id=%s", (id,))
    db.commit()

    # Update room status to available
    if payment.get('room_id'):
        cursor.execute("UPDATE rooms SET status='available' WHERE id=%s", (payment['room_id'],))
        db.commit()

    # Update checkin status to checked-out
    cursor.execute("UPDATE checkins SET status='checked-out' WHERE id=%s", (payment['checkin_id'],))
    db.commit()

    # Delete reservation if linked
    if payment.get('reservation_id'):
        cursor.execute("UPDATE checkins SET reservation_id=NULL WHERE reservation_id=%s", (payment['reservation_id'],))
        db.commit()
        cursor.execute("DELETE FROM reservations WHERE id=%s", (payment['reservation_id'],))
        db.commit()

    cursor.close()
    return redirect(url_for('payments'))

# ==================== ADDONS MANAGEMENT ====================

@app.route('/addons')
@require_login
def addons():
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM addons ORDER BY name")
    addons_list = cursor.fetchall()
    cursor.close()
    return render_template('addons.html', addons=addons_list)

@app.route('/addons/add', methods=['POST'])
@require_login
def add_addon():
    name = request.form['name']
    price = request.form['price']

    cursor = db.cursor()
    cursor.execute("INSERT INTO addons (name, price) VALUES (%s, %s)", (name, price))
    db.commit()
    cursor.close()
    return redirect(url_for('addons'))

@app.route('/addons/<int:id>/edit', methods=['POST'])
@require_login
def edit_addon(id):
    name = request.form['name']
    price = request.form['price']
    available = 'available' in request.form

    cursor = db.cursor()
    cursor.execute("UPDATE addons SET name=%s, price=%s, available=%s WHERE id=%s",
                  (name, price, available, id))
    db.commit()
    cursor.close()
    return redirect(url_for('addons'))

@app.route('/addons/<int:id>/delete', methods=['POST'])
@require_login
def delete_addon(id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM addons WHERE id=%s", (id,))
    db.commit()
    cursor.close()
    return redirect(url_for('addons'))

@app.route('/addons/<int:id>/toggle', methods=['POST'])
@require_login
def toggle_addon(id):
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT available FROM addons WHERE id=%s", (id,))
    addon = cursor.fetchone()
    cursor.close()

    new_status = not addon['available']
    cursor = db.cursor()
    cursor.execute("UPDATE addons SET available=%s WHERE id=%s", (new_status, id))
    db.commit()
    cursor.close()
    return redirect(url_for('addons'))

# ==================== SETTINGS ====================

@app.route('/settings', methods=['GET', 'POST'])
@require_login
def settings():
    # Default to general tab, preserve tab on POST using setting_group
    active_tab = request.form.get('setting_group', 'general') if request.method == 'POST' else 'general'

    if request.method == 'POST':
        cursor = db.cursor()

        # Company settings (general tab)
        if request.form.get('setting_group') == 'general':
            company_name = request.form.get('company_name')
            app_name = request.form.get('app_name')
            company_tax_id = request.form.get('company_tax_id')
            company_address = request.form.get('company_address')
            company_phone = request.form.get('company_phone')
            company_email = request.form.get('company_email')
            company_website = request.form.get('company_website')
            currency = request.form.get('currency')
            currency_symbol = request.form.get('currency_symbol')
            language = request.form.get('language')
            logo_icon = request.form.get('logo_icon')

            general_settings = [
                ('company_name', company_name),
                ('app_name', app_name),
                ('company_tax_id', company_tax_id),
                ('company_address', company_address),
                ('company_phone', company_phone),
                ('company_email', company_email),
                ('company_website', company_website),
                ('currency', currency),
                ('currency_symbol', currency_symbol),
                ('language', language),
                ('logo_icon', logo_icon),
                ('logo_size', request.form.get('logo_size', '44')),
                ('logo_width', request.form.get('logo_width', '')),
                ('tax_rate', request.form.get('tax_rate', '10')),
                ('require_downpayment', request.form.get('require_downpayment', 'false')),
                ('system_timezone', request.form.get('system_timezone', 'UTC'))
            ]
            for key, value in general_settings:
                cursor.execute("INSERT INTO settings (setting_key, setting_value) VALUES (%s, %s) "
                             "ON DUPLICATE KEY UPDATE setting_value=%s", (key, value, value))
            db.commit()

            # Logo upload
            if 'logo' in request.files and request.files['logo'].filename:
                logo_file = request.files['logo']
                import uuid
                ext = logo_file.filename.rsplit('.', 1)[1].lower() if '.' in logo_file.filename else 'png'
                logo_filename = str(uuid.uuid4()) + '.' + ext
                upload_path = os.path.join('static', 'uploads', logo_filename)
                os.makedirs('static/uploads', exist_ok=True)
                logo_file.save(upload_path)
                cursor.execute("INSERT INTO settings (setting_key, setting_value) VALUES ('logo', %s) "
                             "ON DUPLICATE KEY UPDATE setting_value=%s", (logo_filename, logo_filename))
                db.commit()

        # Appearance settings (theme only)
        elif request.form.get('setting_group') == 'appearance':
            theme = request.form.get('theme')
            cursor.execute("INSERT INTO settings (setting_key, setting_value) VALUES ('theme', %s) "
                         "ON DUPLICATE KEY UPDATE setting_value=%s", (theme, theme))
            db.commit()
            active_tab = 'appearance'

        # Permissions settings
        elif request.form.get('setting_group') == 'permissions':
            cursor.execute("INSERT INTO settings (setting_key, setting_value) VALUES ('staff_can_confirm', %s) "
                         "ON DUPLICATE KEY UPDATE setting_value=%s",
                         ('true' if request.form.get('staff_can_confirm') else 'false',
                          'true' if request.form.get('staff_can_confirm') else 'false'))
            cursor.execute("INSERT INTO settings (setting_key, setting_value) VALUES ('staff_can_cancel', %s) "
                         "ON DUPLICATE KEY UPDATE setting_value=%s",
                         ('true' if request.form.get('staff_can_cancel') else 'false',
                          'true' if request.form.get('staff_can_cancel') else 'false'))
            cursor.execute("INSERT INTO settings (setting_key, setting_value) VALUES ('staff_can_delete', %s) "
                         "ON DUPLICATE KEY UPDATE setting_value=%s",
                         ('true' if request.form.get('staff_can_delete') else 'false',
                          'true' if request.form.get('staff_can_delete') else 'false'))
            db.commit()
            active_tab = 'permissions'

        # Email settings
        elif request.form.get('setting_group') == 'email':
            email_settings = [
                ('email_enabled', 'true' if request.form.get('email_enabled') else 'false'),
                ('email_smtp_host', request.form.get('email_smtp_host') or ''),
                ('email_smtp_port', request.form.get('email_smtp_port') or '587'),
                ('email_smtp_user', request.form.get('email_smtp_user') or ''),
                ('email_smtp_password', request.form.get('email_smtp_password') or ''),
                ('email_sender', request.form.get('email_sender') or ''),
                ('email_sender_name', request.form.get('email_sender_name') or ''),
                ('email_confirmation', 'true' if request.form.get('email_confirmation') else 'false'),
                ('email_cancellation', 'true' if request.form.get('email_cancellation') else 'false'),
                ('email_confirmation_subject', request.form.get('email_confirmation_subject') or ''),
                ('email_confirmation_body', request.form.get('email_confirmation_body') or ''),
                ('email_cancellation_subject', request.form.get('email_cancellation_subject') or ''),
                ('email_cancellation_body', request.form.get('email_cancellation_body') or ''),
                ('email_footer', request.form.get('email_footer') or '')
            ]
            for key, value in email_settings:
                cursor.execute("INSERT INTO settings (setting_key, setting_value) VALUES (%s, %s) "
                             "ON DUPLICATE KEY UPDATE setting_value=%s", (key, value, value))
            db.commit()
            active_tab = 'email'

        cursor.close()
        flash('Settings saved successfully!', 'success')
        return redirect(url_for('settings', active_tab=active_tab))

    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM settings")
    all_settings = {row['setting_key']: row['setting_value'] for row in cursor.fetchall()}
    cursor.close()

    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
    users = cursor.fetchall()
    cursor.close()

    # Get active tab from query param or default to general
    active_tab = request.args.get('active_tab', 'general')

    return render_template('settings.html', settings=all_settings, users=users, active_tab=active_tab)

@app.route('/settings/test-email', methods=['POST'])
@require_login
def test_email():
    test_email_address = request.form.get('test_email')
    if not test_email_address:
        flash('Please enter an email address to send the test.', 'danger')
        return redirect(url_for('settings'))

    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT setting_key, setting_value FROM settings WHERE setting_key LIKE 'email_%'")
    settings = {row['setting_key']: row['setting_value'] for row in cursor.fetchall()}
    cursor.close()

    email_enabled = settings.get('email_enabled', 'false') == 'true'
    smtp_host = settings.get('email_smtp_host', '')
    smtp_port = int(settings.get('email_smtp_port', '587') or 587)
    smtp_user = settings.get('email_smtp_user', '')
    smtp_password = settings.get('email_smtp_password', '')
    sender_email = settings.get('email_sender', '')
    sender_name = settings.get('email_sender_name', 'DNZTech IMS')

    if not email_enabled:
        flash('Email is not enabled. Please enable email notifications first.', 'danger')
        return redirect(url_for('settings'))

    if not smtp_host or not smtp_user or not smtp_password or not sender_email:
        flash('SMTP settings are not complete. Please configure all SMTP fields.', 'danger')
        return redirect(url_for('settings'))

    subject = f"Test Email from {sender_name}"
    html_body = f"""
    <h2>{sender_name}</h2>
    <p>This is a test email to verify your SMTP settings are working correctly.</p>
    <p>If you received this email, your email configuration is successful!</p>
    <p><strong>Sent at:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    """

    result = send_email(test_email_address, subject, html_body)

    if result:
        flash(f'Test email sent successfully to {test_email_address}!', 'success')
    else:
        flash('Failed to send test email. Check your SMTP settings and try again.', 'danger')

    return redirect(url_for('settings'))

@app.route('/settings/backup', methods=['POST'])
@require_login
def backup_database():
    import subprocess
    from datetime import datetime

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"backup_{timestamp}.sql"

    try:
        result = subprocess.run([
            'mysqldump',
            '-u', 'root',
            '-p@ kylemadel28',
            'flaskdb'
        ], capture_output=True, text=True)

        with open(filename, 'w') as f:
            f.write(result.stdout)

        return redirect(url_for('settings'))
    except Exception as e:
        return f"Backup failed: {str(e)}"

@app.route('/users/add', methods=['POST'])
@require_login
def add_user():
    email = request.form['email']
    password = request.form['password']
    name = request.form['name']
    role = request.form['role']

    cursor = db.cursor()
    cursor.execute("INSERT INTO users (email, password, name, role) VALUES (%s, %s, %s, %s)",
                  (email, password, name, role))
    db.commit()
    cursor.close()
    return redirect(url_for('settings'))

@app.route('/users/<int:id>/delete', methods=['POST'])
@require_login
def delete_user(id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE id=%s", (id,))
    db.commit()
    cursor.close()
    return redirect(url_for('settings'))

# Helper to get setting
def get_setting(key, default=''):
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT setting_value FROM settings WHERE setting_key=%s", (key,))
    result = cursor.fetchone()
    cursor.close()
    return result['setting_value'] if result else default

def get_tax_rate():
    """Get global tax rate from settings, default 10%"""
    try:
        return float(get_setting('tax_rate', '10'))
    except (ValueError, TypeError):
        return 10.0

# ==================== THEME & CURRENCY HELPER ====================

@app.context_processor
def inject_settings():
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM settings")
    all_settings = {row['setting_key']: row['setting_value'] for row in cursor.fetchall()}
    cursor.close()
    return dict(system_settings=all_settings, user_role=session.get('role', 'staff'))

@app.template_filter('format_currency')
def format_currency(value):
    try:
        val = float(value)
        # If whole number, show without decimals; otherwise show 2 decimals
        if val == int(val):
            return "{:,}".format(int(val))
        return "{:,.2f}".format(val)
    except (ValueError, TypeError):
        return value

@app.template_filter('local_datetime')
def format_local_datetime_filter(dt, format='%Y-%m-%d %H:%M'):
    """Format a datetime in user's timezone"""
    if dt is None:
        return '-'
    try:
        local_dt = to_user_timezone(dt)
        return local_dt.strftime(format)
    except Exception:
        try:
            return dt.strftime(format)
        except Exception:
            return str(dt)

@app.template_filter('user_timezone')
def get_user_timezone_name():
    """Get the user's timezone name for display"""
    return get_setting('system_timezone', 'UTC')

# ==================== REPORTS ====================

@app.route('/reports')
@require_login
def reports():
    cursor = db.cursor(pymysql.cursors.DictCursor)

    # Default to current month
    today = datetime.now()
    start_date = request.args.get('start_date', today.strftime('%Y-%m-01'))
    end_date = request.args.get('end_date', today.strftime('%Y-%m-%d'))
    period = request.args.get('period', 'custom')

    report_type = request.args.get('type', 'reservation')

    # Build date filter based on period
    if period == 'weekly':
        start_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
    elif period == 'monthly':
        start_date = today.strftime('%Y-%m-01')
        end_date = today.strftime('%Y-%m-%d')
    elif period == 'yearly':
        start_date = today.strftime('%Y-01-01')
        end_date = today.strftime('%Y-%m-%d')

    # Reservation Report
    cursor.execute("""
        SELECT r.*, rom.room_number, rom.type
        FROM reservations r
        JOIN rooms rom ON r.room_id = rom.id
        WHERE DATE(r.created_at) BETWEEN %s AND %s
        ORDER BY r.created_at DESC
    """, (start_date, end_date))
    reservation_data = cursor.fetchall()

    # Sales Report (Payments)
    cursor.execute("""
        SELECT p.*, c.guest_name, rom.room_number, rom.type
        FROM payments p
        JOIN checkins c ON p.checkin_id = c.id
        JOIN rooms rom ON c.room_id = rom.id
        WHERE p.status = 'completed' AND DATE(p.created_at) BETWEEN %s AND %s
        ORDER BY p.created_at DESC
    """, (start_date, end_date))
    sales_data = cursor.fetchall()

    # Guest Report (Check-ins)
    cursor.execute("""
        SELECT c.*, rom.room_number, rom.type
        FROM checkins c
        JOIN rooms rom ON c.room_id = rom.id
        WHERE DATE(c.check_in_time) BETWEEN %s AND %s
        ORDER BY c.check_in_time DESC
    """, (start_date, end_date))
    guest_data = cursor.fetchall()

    # Foods Menu Report
    cursor.execute("SELECT * FROM foods ORDER BY category, name")
    foods_data = cursor.fetchall()

    # Addons Report
    cursor.execute("SELECT * FROM addons ORDER BY name")
    addons_data = cursor.fetchall()

    # Food Orders Report
    cursor.execute("""
        SELECT fo.*, c.guest_name, rom.room_number
        FROM food_orders fo
        JOIN checkins c ON fo.checkin_id = c.id
        JOIN rooms rom ON c.room_id = rom.id
        WHERE DATE(fo.order_time) BETWEEN %s AND %s
        ORDER BY fo.order_time DESC
    """, (start_date, end_date))
    food_orders_data = cursor.fetchall()

    # Addon Orders Report
    cursor.execute("""
        SELECT ao.*, c.guest_name, rom.room_number, ad.name as addon_name
        FROM addon_orders ao
        JOIN checkins c ON ao.checkin_id = c.id
        JOIN rooms rom ON c.room_id = rom.id
        JOIN addons ad ON ao.addon_id = ad.id
        WHERE DATE(ao.order_time) BETWEEN %s AND %s
        ORDER BY ao.order_time DESC
    """, (start_date, end_date))
    addon_orders_data = cursor.fetchall()

    # Summary stats
    cursor.execute("""
        SELECT COUNT(*) as total FROM reservations
        WHERE DATE(created_at) BETWEEN %s AND %s
    """, (start_date, end_date))
    total_reservations = cursor.fetchone()['total']

    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0) as total FROM payments
        WHERE status = 'completed' AND DATE(created_at) BETWEEN %s AND %s
    """, (start_date, end_date))
    total_sales = cursor.fetchone()['total']

    cursor.execute("""
        SELECT COUNT(*) as total FROM checkins
        WHERE DATE(check_in_time) BETWEEN %s AND %s
    """, (start_date, end_date))
    total_guests = cursor.fetchone()['total']

    cursor.execute("""
        SELECT COALESCE(SUM(quantity * price), 0) as total FROM food_orders
        WHERE DATE(order_time) BETWEEN %s AND %s
    """, (start_date, end_date))
    total_food_sales = cursor.fetchone()['total']

    cursor.close()

    return render_template('reports.html',
                         reservation_data=reservation_data,
                         sales_data=sales_data,
                         guest_data=guest_data,
                         foods_data=foods_data,
                         addons_data=addons_data,
                         food_orders_data=food_orders_data,
                         addon_orders_data=addon_orders_data,
                         start_date=start_date,
                         end_date=end_date,
                         period=period,
                         report_type=report_type,
                         total_reservations=total_reservations,
                         total_sales=total_sales,
                         total_guests=total_guests,
                         total_food_sales=total_food_sales)

@app.route('/reports/export/<format>')
@require_login
def export_report(format):
    from flask import make_response
    import csv
    import io

    cursor = db.cursor(pymysql.cursors.DictCursor)

    start_date = request.args.get('start_date', datetime.now().strftime('%Y-%m-01'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    report_type = request.args.get('type', 'reservation')

    output = io.StringIO()

    if report_type == 'reservation':
        cursor.execute("""
            SELECT r.guest_name, r.email, r.phone, rom.room_number, rom.type,
                   r.check_in, r.check_out, r.status, r.created_at
            FROM reservations r
            JOIN rooms rom ON r.room_id = rom.id
            WHERE DATE(r.created_at) BETWEEN %s AND %s
            ORDER BY r.created_at DESC
        """, (start_date, end_date))
        data = cursor.fetchall()
        filename = 'reservation_report'

        if format == 'csv':
            writer = csv.writer(output)
            writer.writerow(['Guest Name', 'Email', 'Phone', 'Room', 'Type', 'Check-in', 'Check-out', 'Status', 'Created'])
            for row in data:
                writer.writerow([row['guest_name'], row['email'], row['phone'], row['room_number'],
                               row['type'], row['check_in'], row['check_out'], row['status'], row['created_at']])
            output.seek(0)
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename={filename}.csv'

    elif report_type == 'sales':
        cursor.execute("""
            SELECT p.id, c.guest_name, rom.room_number, p.amount, p.payment_type, p.status, p.created_at
            FROM payments p
            JOIN checkins c ON p.checkin_id = c.id
            JOIN rooms rom ON c.room_id = rom.id
            WHERE p.status = 'completed' AND DATE(p.created_at) BETWEEN %s AND %s
            ORDER BY p.created_at DESC
        """, (start_date, end_date))
        data = cursor.fetchall()
        filename = 'sales_report'

        if format == 'csv':
            writer = csv.writer(output)
            writer.writerow(['ID', 'Guest', 'Room', 'Amount', 'Payment Type', 'Status', 'Date'])
            for row in data:
                writer.writerow([row['id'], row['guest_name'], row['room_number'], row['amount'],
                               row['payment_type'], row['status'], row['created_at']])
            output.seek(0)
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename={filename}.csv'

    elif report_type == 'guest':
        cursor.execute("""
            SELECT c.guest_name, c.check_in_time, c.check_out_time, rom.room_number, rom.type, c.status
            FROM checkins c
            JOIN rooms rom ON c.room_id = rom.id
            WHERE DATE(c.check_in_time) BETWEEN %s AND %s
            ORDER BY c.check_in_time DESC
        """, (start_date, end_date))
        data = cursor.fetchall()
        filename = 'guest_report'

        if format == 'csv':
            writer = csv.writer(output)
            writer.writerow(['Guest Name', 'Check-in', 'Check-out', 'Room', 'Type', 'Status'])
            for row in data:
                writer.writerow([row['guest_name'], row['check_in_time'], row['check_out_time'],
                               row['room_number'], row['type'], row['status']])
            output.seek(0)
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename={filename}.csv'

    elif report_type == 'foods':
        cursor.execute("SELECT * FROM foods ORDER BY category, name")
        data = cursor.fetchall()
        filename = 'foods_menu_report'

        if format == 'csv':
            writer = csv.writer(output)
            writer.writerow(['Name', 'Price', 'Category'])
            for row in data:
                writer.writerow([row['name'], row['price'], row['category']])
            output.seek(0)
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename={filename}.csv'

    elif report_type == 'addons':
        cursor.execute("SELECT * FROM addons ORDER BY name")
        data = cursor.fetchall()
        filename = 'addons_report'

        if format == 'csv':
            writer = csv.writer(output)
            writer.writerow(['Name', 'Price'])
            for row in data:
                writer.writerow([row['name'], row['price']])
            output.seek(0)
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename={filename}.csv'

    elif report_type == 'food_orders':
        cursor.execute("""
            SELECT fo.*, c.guest_name, rom.room_number
            FROM food_orders fo
            JOIN checkins c ON fo.checkin_id = c.id
            JOIN rooms rom ON c.room_id = rom.id
            WHERE DATE(fo.order_time) BETWEEN %s AND %s
            ORDER BY fo.order_time DESC
        """, (start_date, end_date))
        data = cursor.fetchall()
        filename = 'food_orders_report'

        if format == 'csv':
            writer = csv.writer(output)
            writer.writerow(['Guest', 'Room', 'Item', 'Quantity', 'Price', 'Total', 'Order Time'])
            for row in data:
                writer.writerow([row['guest_name'], row['room_number'], row['item_name'],
                               row['quantity'], row['price'], row['quantity'] * row['price'],
                               row['order_time']])
            output.seek(0)
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename={filename}.csv'

    elif report_type == 'addon_orders':
        cursor.execute("""
            SELECT ao.*, c.guest_name, rom.room_number, ad.name as addon_name
            FROM addon_orders ao
            JOIN checkins c ON ao.checkin_id = c.id
            JOIN rooms rom ON c.room_id = rom.id
            JOIN addons ad ON ao.addon_id = ad.id
            WHERE DATE(ao.order_time) BETWEEN %s AND %s
            ORDER BY ao.order_time DESC
        """, (start_date, end_date))
        data = cursor.fetchall()
        filename = 'addon_orders_report'

        if format == 'csv':
            writer = csv.writer(output)
            writer.writerow(['Guest', 'Room', 'Addon', 'Quantity', 'Price', 'Total', 'Status', 'Date'])
            for row in data:
                writer.writerow([row['guest_name'], row['room_number'], row['addon_name'],
                               row['quantity'], row['price'], row['quantity'] * row['price'],
                               row['status'], row['created_at']])
            output.seek(0)
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename={filename}.csv'

    else:
        response = make_response("Invalid report type")
        response.headers['Content-Type'] = 'text/plain'

    cursor.close()
    return response

# ==================== EMAIL HELPER ====================

def get_email_settings():
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT setting_key, setting_value FROM settings WHERE setting_key LIKE 'email_%'")
    settings = {row['setting_key']: row['setting_value'] for row in cursor.fetchall()}
    cursor.close()
    return {
        'enabled': settings.get('email_enabled', 'false') == 'true',
        'smtp_host': settings.get('email_smtp_host', 'smtp.gmail.com'),
        'smtp_port': int(settings.get('email_smtp_port', '587')),
        'smtp_user': settings.get('email_smtp_user', ''),
        'smtp_password': settings.get('email_smtp_password', ''),
        'sender_email': settings.get('email_sender', ''),
        'sender_name': settings.get('email_sender_name', 'DNZTech IMS')
    }

def render_email_template(template, replacements):
    """Replace placeholders in email template with actual values"""
    for key, value in replacements.items():
        template = template.replace('{' + key + '}', str(value))
    return template

def send_email(to_email, subject, html_body, text_body=None):
    print(f"[EMAIL] Starting send_email to: {to_email}")

    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT setting_key, setting_value FROM settings WHERE setting_key LIKE 'email_%'")
    settings = {row['setting_key']: row['setting_value'] for row in cursor.fetchall()}
    cursor.close()

    email_enabled = settings.get('email_enabled', 'false') == 'true'
    smtp_host = settings.get('email_smtp_host', '')
    smtp_port = int(settings.get('email_smtp_port', '587') or 587)
    smtp_user = settings.get('email_smtp_user', '')
    smtp_password = settings.get('email_smtp_password', '')
    sender_email = settings.get('email_sender', '')
    sender_name = settings.get('email_sender_name', 'DNZTech IMS')

    print(f"[EMAIL] Settings - enabled: {email_enabled}, host: {smtp_host}, port: {smtp_port}")
    print(f"[EMAIL] Credentials - user: {smtp_user}, sender: {sender_email}")

    if not email_enabled:
        print("[EMAIL] Disabled, skipping")
        return False

    if not to_email:
        print("[EMAIL] No recipient email")
        return False

    if not smtp_host or not smtp_user or not smtp_password or not sender_email:
        print("[EMAIL] Missing SMTP configuration")
        return False

    if text_body is None:
        text_body = html_body.replace('<br>', '\n').replace('<p>', '').replace('</p>', '\n')

    msg = MIMEMultipart('alternative')
    msg['From'] = f"{sender_name} <{sender_email}>"
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))

    try:
        print(f"[EMAIL] Connecting to {smtp_host}:{smtp_port}...")
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
        server.set_debuglevel(1)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_user, smtp_password)
        server.sendmail(sender_email, [to_email], msg.as_string())
        server.quit()
        print("[EMAIL] Sent successfully!")
        return True
    except Exception as e:
        print(f"[EMAIL] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

@app.route('/migrate/add-image-column')
@require_login
def migrate_add_image_column():
    cursor = db.cursor()
    try:
        cursor.execute("ALTER TABLE foods ADD COLUMN image VARCHAR(255) DEFAULT NULL")
        db.commit()
        cursor.close()
        return "Image column added successfully"
    except Exception as e:
        cursor.close()
        return f"Error: {str(e)}"

@app.route('/migrate/add-room-image-column')
@require_login
def migrate_add_room_image_column():
    cursor = db.cursor()
    try:
        cursor.execute("ALTER TABLE rooms ADD COLUMN image VARCHAR(255) DEFAULT NULL")
        db.commit()
        cursor.close()
        return "Room image column added successfully"
    except Exception as e:
        cursor.close()
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
