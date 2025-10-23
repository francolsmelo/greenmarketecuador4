import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Product, AdminUser, SiteConfig, User, Order, PaymentMethod
from functools import wraps
from PIL import Image
import stripe
import paypalrestsdk
from flask_mail import Mail, Message

app = Flask(__name__)

if not os.environ.get("SESSION_SECRET"):
    raise ValueError("SESSION_SECRET environment variable must be set")

app.secret_key = os.environ.get("SESSION_SECRET")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

paypalrestsdk.configure({
    "mode": os.environ.get("PAYPAL_MODE", "sandbox"),
    "client_id": os.environ.get("PAYPAL_CLIENT_ID"),
    "client_secret": os.environ.get("PAYPAL_CLIENT_SECRET")
})

app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@greenmarket.com')

mail = Mail(app)

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'static/uploads'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

db.init_app(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)
os.makedirs('templates', exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Por favor inicia sesión para acceder al panel de administración', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            subject = request.form.get('subject', '').strip()
            message_text = request.form.get('message', '').strip()
            
            if not name or not email or not subject or not message_text:
                flash('Por favor completa todos los campos obligatorios', 'error')
                return render_template('contact.html')
            
            msg = Message(
                subject=f"[GreenMarket] {subject}",
                recipients=['klinfra@yahoo.com'],
                reply_to=email
            )
            
            msg.body = f"""
Nuevo mensaje de contacto desde GreenMarket Ecuador

Nombre: {name}
Email: {email}
Teléfono: {phone if phone else 'No proporcionado'}

Asunto: {subject}

Mensaje:
{message_text}

---
Este mensaje fue enviado desde el formulario de contacto de GreenMarket Ecuador.
            """
            
            msg.html = f"""
<h2>Nuevo mensaje de contacto desde GreenMarket Ecuador</h2>

<p><strong>Nombre:</strong> {name}</p>
<p><strong>Email:</strong> <a href="mailto:{email}">{email}</a></p>
<p><strong>Teléfono:</strong> {phone if phone else 'No proporcionado'}</p>

<h3>Asunto: {subject}</h3>

<div style="padding: 20px; background-color: #f5f5f5; border-left: 4px solid #2d7a3e;">
    <p style="white-space: pre-wrap;">{message_text}</p>
</div>

<hr>
<p style="color: #666; font-size: 12px;">Este mensaje fue enviado desde el formulario de contacto de GreenMarket Ecuador.</p>
            """
            
            mail.send(msg)
            flash('¡Tu mensaje ha sido enviado exitosamente! Te responderemos pronto.', 'success')
            return redirect(url_for('contact'))
            
        except Exception as e:
            flash(f'Error al enviar el mensaje: {str(e)}. Por favor intenta contactarnos directamente por teléfono o email.', 'error')
            return render_template('contact.html')
    
    return render_template('contact.html')

@app.route('/checkout/<int:product_id>')
def checkout(product_id):
    product = Product.query.get_or_404(product_id)
    if product.stock <= 0:
        flash('Este producto está agotado', 'error')
        return redirect(url_for('product_detail', product_id=product_id))
    return render_template('checkout.html', product=product)

@app.route('/create-stripe-checkout/<int:product_id>', methods=['POST'])
def create_stripe_checkout(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        
        if product.stock <= 0:
            flash('Este producto está agotado', 'error')
            return redirect(url_for('product_detail', product_id=product_id))
        
        domain_url = request.host_url.rstrip('/')
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product.name,
                        'description': product.description[:500],
                    },
                    'unit_amount': int(product.price * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=domain_url + url_for('payment_success'),
            cancel_url=domain_url + url_for('payment_cancel'),
        )
        
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        flash(f'Error al procesar el pago: {str(e)}', 'error')
        return redirect(url_for('checkout', product_id=product_id))

@app.route('/create-paypal-order/<int:product_id>', methods=['POST'])
def create_paypal_order(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        
        if product.stock <= 0:
            flash('Este producto está agotado', 'error')
            return redirect(url_for('product_detail', product_id=product_id))
        
        domain_url = request.host_url.rstrip('/')
        
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": domain_url + url_for('execute_paypal_payment', product_id=product.id),
                "cancel_url": domain_url + url_for('payment_cancel')
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": product.name,
                        "sku": str(product.id),
                        "price": f"{product.price:.2f}",
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": f"{product.price:.2f}",
                    "currency": "USD"
                },
                "description": product.description[:127]
            }]
        })
        
        if payment.create():
            for link in payment.links:
                if link.rel == "approval_url":
                    return redirect(str(link.href))
        else:
            flash(f'Error al crear el pago de PayPal: {payment.error}', 'error')
            return redirect(url_for('checkout', product_id=product_id))
            
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('checkout', product_id=product_id))

@app.route('/execute-paypal-payment/<int:product_id>')
def execute_paypal_payment(product_id):
    payment_id = request.args.get('paymentId')
    payer_id = request.args.get('PayerID')
    
    try:
        payment = paypalrestsdk.Payment.find(payment_id)
        
        if payment.execute({"payer_id": payer_id}):
            product = Product.query.get_or_404(product_id)
            if product.stock > 0:
                product.stock -= 1
                db.session.commit()
            flash('¡Pago completado exitosamente con PayPal!', 'success')
            return redirect(url_for('payment_success'))
        else:
            flash(f'Error al ejecutar el pago: {payment.error}', 'error')
            return redirect(url_for('payment_cancel'))
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('payment_cancel'))

@app.route('/payment/success')
def payment_success():
    return render_template('payment_success.html')

@app.route('/payment/cancel')
def payment_cancel():
    return render_template('payment_cancel.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Por favor ingresa usuario y contraseña', 'error')
            return render_template('admin_login.html')
        
        admin = AdminUser.query.filter_by(username=username).first()
        
        if admin and check_password_hash(admin.password, password):
            session['admin_logged_in'] = True
            session['admin_username'] = username
            session['admin_id'] = admin.id
            flash('¡Bienvenido al panel de administración!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Credenciales incorrectas', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    products = Product.query.all()
    return render_template('admin_dashboard.html', products=products)

@app.route('/admin/product/add', methods=['GET', 'POST'])
@login_required
def admin_add_product():
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            
            if not name or not description:
                flash('El nombre y la descripción son obligatorios', 'error')
                return render_template('admin_add_product.html')
            
            try:
                price = float(request.form.get('price', 0))
                stock = int(request.form.get('stock', 0))
            except (ValueError, TypeError):
                flash('Precio y stock deben ser valores numéricos válidos', 'error')
                return render_template('admin_add_product.html')
            
            if price < 0 or stock < 0:
                flash('El precio y stock no pueden ser negativos', 'error')
                return render_template('admin_add_product.html')
            
            image_filename = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename and allowed_file(file.filename):
                    try:
                        filename = secure_filename(file.filename)
                        timestamp = str(int(os.times()[4] * 1000))
                        filename = f"{timestamp}_{filename}"
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        
                        img = Image.open(file.stream)
                        img.thumbnail((800, 800))
                        img.save(filepath, optimize=True, quality=85)
                        
                        image_filename = filename
                    except Exception as e:
                        flash(f'Error al procesar la imagen: {str(e)}', 'error')
                        return render_template('admin_add_product.html')
            
            product = Product()
            product.name = name
            product.description = description
            product.price = price
            product.stock = stock
            product.image_filename = image_filename
            
            db.session.add(product)
            db.session.commit()
            
            flash('Producto agregado exitosamente', 'success')
            return redirect(url_for('admin_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar el producto: {str(e)}', 'error')
            return render_template('admin_add_product.html')
    
    return render_template('admin_add_product.html')

@app.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            
            if not name or not description:
                flash('El nombre y la descripción son obligatorios', 'error')
                return render_template('admin_edit_product.html', product=product)
            
            try:
                price = float(request.form.get('price', 0))
                stock = int(request.form.get('stock', 0))
            except (ValueError, TypeError):
                flash('Precio y stock deben ser valores numéricos válidos', 'error')
                return render_template('admin_edit_product.html', product=product)
            
            if price < 0 or stock < 0:
                flash('El precio y stock no pueden ser negativos', 'error')
                return render_template('admin_edit_product.html', product=product)
            
            product.name = name
            product.description = description
            product.price = price
            product.stock = stock
            
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename and allowed_file(file.filename):
                    try:
                        if product.image_filename:
                            old_path = os.path.join(app.config['UPLOAD_FOLDER'], product.image_filename)
                            if os.path.exists(old_path):
                                os.remove(old_path)
                        
                        filename = secure_filename(file.filename)
                        timestamp = str(int(os.times()[4] * 1000))
                        filename = f"{timestamp}_{filename}"
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        
                        img = Image.open(file.stream)
                        img.thumbnail((800, 800))
                        img.save(filepath, optimize=True, quality=85)
                        
                        product.image_filename = filename
                    except Exception as e:
                        flash(f'Error al procesar la imagen: {str(e)}', 'error')
                        return render_template('admin_edit_product.html', product=product)
            
            db.session.commit()
            flash('Producto actualizado exitosamente', 'success')
            return redirect(url_for('admin_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el producto: {str(e)}', 'error')
            return render_template('admin_edit_product.html', product=product)
    
    return render_template('admin_edit_product.html', product=product)

@app.route('/admin/product/delete/<int:product_id>', methods=['POST'])
@login_required
def admin_delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if product.image_filename:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], product.image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(product)
    db.session.commit()
    
    flash('Producto eliminado exitosamente', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/customization', methods=['GET', 'POST'])
@login_required
def admin_customization():
    if request.method == 'POST':
        try:
            primary_color = request.form.get('primary_color', '#2d7a3e')
            secondary_color = request.form.get('secondary_color', '#4caf50')
            light_color = request.form.get('light_color', '#81c784')
            bg_color = request.form.get('bg_color', '#f5f5f5')
            
            configs = {
                'primary_color': primary_color,
                'secondary_color': secondary_color,
                'light_color': light_color,
                'bg_color': bg_color
            }
            
            for key, value in configs.items():
                config = SiteConfig.query.filter_by(config_key=key).first()
                if config:
                    config.config_value = value
                else:
                    config = SiteConfig(config_key=key, config_value=value)
                    db.session.add(config)
            
            db.session.commit()
            flash('Configuración visual actualizada exitosamente', 'success')
            return redirect(url_for('admin_customization'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la configuración: {str(e)}', 'error')
    
    configs = {}
    for key in ['primary_color', 'secondary_color', 'light_color', 'bg_color']:
        config = SiteConfig.query.filter_by(config_key=key).first()
        configs[key] = config.config_value if config else ''
    
    return render_template('admin_customization.html', configs=configs)

@app.route('/admin/payments', methods=['GET', 'POST'])
@login_required
def admin_payments():
    if request.method == 'POST':
        try:
            action = request.form.get('action')
            
            if action == 'toggle':
                payment_id = int(request.form.get('payment_id'))
                payment = PaymentMethod.query.get_or_404(payment_id)
                payment.enabled = not payment.enabled
                db.session.commit()
                flash(f'Método de pago {payment.name} {"activado" if payment.enabled else "desactivado"}', 'success')
            
            elif action == 'update_order':
                for key, value in request.form.items():
                    if key.startswith('order_'):
                        payment_id = int(key.split('_')[1])
                        payment = PaymentMethod.query.get(payment_id)
                        if payment:
                            payment.display_order = int(value)
                db.session.commit()
                flash('Orden de visualización actualizado', 'success')
            
            return redirect(url_for('admin_payments'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
    
    payments = PaymentMethod.query.order_by(PaymentMethod.display_order).all()
    return render_template('admin_payments.html', payments=payments)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            full_name = request.form.get('full_name', '').strip()
            phone = request.form.get('phone', '').strip()
            
            if not email or not username or not password:
                flash('Email, usuario y contraseña son obligatorios', 'error')
                return render_template('register.html')
            
            if password != confirm_password:
                flash('Las contraseñas no coinciden', 'error')
                return render_template('register.html')
            
            if len(password) < 6:
                flash('La contraseña debe tener al menos 6 caracteres', 'error')
                return render_template('register.html')
            
            if User.query.filter_by(email=email).first():
                flash('El email ya está registrado', 'error')
                return render_template('register.html')
            
            if User.query.filter_by(username=username).first():
                flash('El nombre de usuario ya está en uso', 'error')
                return render_template('register.html')
            
            user = User()
            user.email = email
            user.username = username
            user.password = generate_password_hash(password)
            user.full_name = full_name
            user.phone = phone
            
            db.session.add(user)
            db.session.commit()
            
            flash('¡Registro exitoso! Ya puedes iniciar sesión', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar: {str(e)}', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username_or_email or not password:
            flash('Por favor ingresa usuario/email y contraseña', 'error')
            return render_template('login.html')
        
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email.lower())
        ).first()
        
        if user and check_password_hash(user.password, password):
            session['user_logged_in'] = True
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'¡Bienvenido {user.full_name or user.username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Credenciales incorrectas', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_logged_in', None)
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_logged_in' not in session:
        flash('Debes iniciar sesión para ver tu perfil', 'error')
        return redirect(url_for('login'))
    
    user = User.query.get_or_404(session['user_id'])
    
    if request.method == 'POST':
        try:
            action = request.form.get('action')
            
            if action == 'update_profile':
                user.full_name = request.form.get('full_name', '').strip()
                user.phone = request.form.get('phone', '').strip()
                user.address = request.form.get('address', '').strip()
                db.session.commit()
                flash('Perfil actualizado exitosamente', 'success')
            
            elif action == 'change_password':
                current_password = request.form.get('current_password', '')
                new_password = request.form.get('new_password', '')
                confirm_password = request.form.get('confirm_password', '')
                
                if not check_password_hash(user.password, current_password):
                    flash('Contraseña actual incorrecta', 'error')
                elif new_password != confirm_password:
                    flash('Las contraseñas nuevas no coinciden', 'error')
                elif len(new_password) < 6:
                    flash('La contraseña debe tener al menos 6 caracteres', 'error')
                else:
                    user.password = generate_password_hash(new_password)
                    db.session.commit()
                    flash('Contraseña actualizada exitosamente', 'success')
            
            return redirect(url_for('profile'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'error')
    
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    return render_template('profile.html', user=user, orders=orders)

def init_defaults():
    with app.app_context():
        admin = AdminUser.query.filter_by(username='admin').first()
        if not admin:
            admin = AdminUser()
            admin.username = 'admin'
            admin.password = generate_password_hash('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully: username='admin', password='admin123'")
        
        if PaymentMethod.query.count() == 0:
            payment_methods = [
                PaymentMethod(name='Stripe (Tarjeta)', enabled=True, display_order=1),
                PaymentMethod(name='PayPal', enabled=True, display_order=2),
                PaymentMethod(name='Contacto Personal', enabled=True, display_order=3)
            ]
            for pm in payment_methods:
                db.session.add(pm)
            db.session.commit()
            print("Payment methods initialized")

with app.app_context():
    db.create_all()
    init_defaults()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
