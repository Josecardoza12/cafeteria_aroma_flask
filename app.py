import os
from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify, abort
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_wtf.csrf import CSRFProtect
from models import db, User, Product, Category, Order, OrderItem, Role
from forms import LoginForm, RegisterForm, ProductForm, CategoryForm
from utils import role_required
from seed_data import seed_db


# Inicialización de extensiones
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = "login"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "clave-super-secreta-123")
    app.config.from_object("config.Config")

    # Inicializar extensiones
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Crear tablas si no existen
    with app.app_context():
        db.create_all()
        seed_db()
        

    # -------------------- RUTAS --------------------

    @app.route("/")
    def index():
        featured = Product.query.filter_by(is_active=True).limit(6).all()
        categories = Category.query.all()
        return render_template("index.html", featured=featured, categories=categories)

    @app.route("/menu")
    def menu():
        cat_id = request.args.get("category", type=int)
        categories = Category.query.all()
        products_query = Product.query.filter_by(is_active=True)
        if cat_id:
            products_query = products_query.filter_by(category_id=cat_id)
        products = products_query.order_by(Product.name.asc()).all()
        return render_template("menu.html", products=products, categories=categories, selected=cat_id)

    # ---------- Autenticación ----------
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("index"))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data.lower()).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                flash(f"¡Bienvenido {user.name}!", "success")
                return redirect(url_for("index"))
            flash("Credenciales inválidas", "danger")
        return render_template("auth/login.html", form=form)

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("index"))
        form = RegisterForm()
        if form.validate_on_submit():
            if User.query.filter_by(email=form.email.data.lower()).first():
                flash("Ese email ya está registrado", "warning")
            else:
                u = User(name=form.name.data.strip(), email=form.email.data.lower(), role=Role.CUSTOMER)
                u.set_password(form.password.data)
                db.session.add(u)
                db.session.commit()
                flash("Cuenta creada. Ahora puedes iniciar sesión.", "success")
                return redirect(url_for("login"))
        return render_template("auth/register.html", form=form)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("Sesión cerrada.", "info")
        return redirect(url_for("index"))

    # ---------- Carrito ----------
    def _get_cart():
        return session.setdefault("cart", {})

    @app.route("/cart")
    def cart():
        cart = _get_cart()
        items = []
        total = 0.0
        for pid, qty in cart.items():
            product = db.session.get(Product, int(pid))
            if not product:
                continue
            line_total = product.price * qty
            items.append({"product": product, "qty": qty, "line_total": line_total})
            total += line_total
        return render_template("cart.html", items=items, total=total)

    @app.post("/cart/add/<int:product_id>")
    def cart_add(product_id):
        product = db.session.get(Product, product_id)
        if not product or not product.is_active or product.stock <= 0:
            abort(400)
        cart = _get_cart()
        cart[str(product_id)] = cart.get(str(product_id), 0) + 1
        session.modified = True
        return jsonify({"ok": True, "cart_count": sum(cart.values())})

    @app.post("/cart/update/<int:product_id>")
    def cart_update(product_id):
        qty = request.form.get("qty", type=int)
        cart = _get_cart()
        if qty is None or qty < 0:
            abort(400)
        if qty == 0:
            cart.pop(str(product_id), None)
        else:
            cart[str(product_id)] = qty
        session.modified = True
        return redirect(url_for("cart"))

    # ---------- Checkout & Pedidos ----------
    @app.route("/checkout", methods=["GET", "POST"])
    @login_required
    def checkout():
        cart = _get_cart()
        if request.method == "POST":
            if not cart:
                flash("Tu carrito está vacío.", "warning")
                return redirect(url_for("menu"))
            payment_method = request.form.get("payment_method", "efectivo")
            order = Order(user_id=current_user.id, status="pendiente", payment_method=payment_method)
            total = 0.0
            for pid, qty in cart.items():
                product = db.session.get(Product, int(pid))
                if not product or not product.is_active or product.stock < qty:
                    flash(f"Stock insuficiente para {product.name if product else 'producto'}", "danger")
                    return redirect(url_for("cart"))
                item = OrderItem(order=order, product=product, quantity=qty, unit_price=product.price)
                db.session.add(item)
                product.stock -= qty
                total += product.price * qty
            order.total = total
            db.session.add(order)
            db.session.commit()
            session["cart"] = {}
            session.modified = True
            flash("¡Pedido realizado! Puedes seguir su estado.", "success")
            return redirect(url_for("order_tracking", order_id=order.id))

        items = []
        total = 0.0
        for pid, qty in cart.items():
            product = db.session.get(Product, int(pid))
            if not product:
                continue
            line_total = product.price * qty
            items.append({"product": product, "qty": qty, "line_total": line_total})
            total += line_total
        return render_template("checkout.html", items=items, total=total)

    @app.get("/orders/<int:order_id>")
    @login_required
    def order_tracking(order_id):
        order = db.session.get(Order, order_id)
        if not order or (not current_user.is_admin() and not current_user.is_employee() and order.user_id != current_user.id):
            abort(404)
        return render_template("order_tracking.html", order=order)

    # ---------- Panel Empleado ----------
    @app.get("/empleado/pedidos")
    @login_required
    @role_required(Role.EMPLOYEE, Role.ADMIN)
    def employee_orders():
        orders = Order.query.filter(Order.status != "cancelado").order_by(Order.created_at.asc()).all()
        return render_template("employee/orders.html", orders=orders)

    @app.post("/empleado/pedidos/<int:order_id>/avanzar")
    @login_required
    @role_required(Role.EMPLOYEE, Role.ADMIN)
    def employee_advance(order_id):
        order = db.session.get(Order, order_id)
        if not order:
            abort(404)
        next_map = {"pendiente": "preparando", "preparando": "listo", "listo": "entregado"}
        order.status = next_map.get(order.status, order.status)
        db.session.commit()
        return redirect(url_for("employee_orders"))

    @app.post("/empleado/pedidos/<int:order_id>/cancelar")
    @login_required
    @role_required(Role.EMPLOYEE, Role.ADMIN)
    def employee_cancel(order_id):
        order = db.session.get(Order, order_id)
        if not order:
            abort(404)
        order.status = "cancelado"
        for it in order.items:
            it.product.stock += it.quantity
        db.session.commit()
        flash(f"Pedido #{order.id} cancelado.", "info")
        return redirect(url_for("employee_orders"))
    @app.route("/testdb")
    def testdb():
        from models import db
        try:
            db.session.execute("SELECT 1")
            return "✅ Conexión exitosa con PostgreSQL"
        except Exception as e:
            return f"❌ Error: {e}"


    return app


# ------------- MAIN ENTRY POINT -------------
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
else:
    app = create_app()
