import os
from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify, abort
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_wtf.csrf import CSRFProtect
from config import Config
from models import db, User, Product, Category, Order, OrderItem, Role
from forms import LoginForm, RegisterForm, ProductForm, CategoryForm
from seed_data import seed_db
from werkzeug.routing import BuildError
from flask import url_for, render_template


# --- Inicialización de extensiones ---
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = "login"


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # --- Extensiones ---
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # --- Crear tablas y cargar seed si es necesario ---
    with app.app_context():
        db.create_all()
        seed_db()

        # Verificar que cada producto tenga una imagen
        productos = Product.query.all()
        for p in productos:
            print(p.name, "→", p.image_url)

            # Si falta una imagen, asignar por defecto
            if not p.image_url:
                nombre = p.name.lower()
                if "capuccino" in nombre:
                    p.image_url = "capuccino.jpg"
                elif "latte" in nombre:
                    p.image_url = "latte.jpg"
                elif "brownie" in nombre:
                    p.image_url = "brownie.jpg"
                elif "sandwich pollo" in nombre:
                    p.image_url = "sandwich_pollo.jpg"
                elif "medialuna" in nombre:
                    p.image_url = "medialuna.jpg"
                elif "frappe_moka" in nombre:
                    p.image_url = "frappe_moka.jpg"
                elif "muffin_choco" in nombre:
                    p.image_url = "muffin_choco.jpg"
                elif "galletas" in nombre:
                    p.image_url = "galletas.jpg"
                elif "cheesecake" in nombre:
                    p.image_url = "cheesecake.jpg"
                elif "te_matcha" in nombre:
                    p.image_url = "te_matcha.jpg"   
                db.session.commit()

    # =================== RUTAS ===================

    @app.route("/")
    def index():
        featured = Product.query.filter_by(is_active=True).limit(6).all()
        categories = Category.query.all()
        return render_template("index.html", featured=featured, categories=categories)

    @app.route("/menu")
    def menu():
        cat_id = request.args.get("category", type=int)
        categories = Category.query.all()
        q = Product.query.filter_by(is_active=True)
        if cat_id:
            q = q.filter_by(category_id=cat_id)
        products = q.order_by(Product.name.asc()).all()
        return render_template("menu.html", products=products, categories=categories, selected=cat_id)

    # --- Autenticación ---
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

    # --- Carrito ---
    def _get_cart():
        return session.setdefault("cart", {})

    @app.route("/cart")
    def cart():
        cart = _get_cart()
        items, total = [], 0.0
        for pid, qty in cart.items():
            p = db.session.get(Product, int(pid))
            if not p:
                continue
            line_total = p.price * qty
            items.append({"product": p, "qty": qty, "line_total": line_total})
            total += line_total
        return render_template("cart.html", items=items, total=total)

    @app.post("/cart/add/<int:product_id>")
    def cart_add(product_id):
        p = db.session.get(Product, product_id)
        if not p or not p.is_active or p.stock <= 0:
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

    # --- Checkout ---
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
                p = db.session.get(Product, int(pid))
                if not p or not p.is_active or p.stock < qty:
                    flash(f"Stock insuficiente para {p.name if p else 'producto'}", "danger")
                    return redirect(url_for("cart"))
                db.session.add(OrderItem(order=order, product=p, quantity=qty, unit_price=p.price))
                p.stock -= qty
                total += p.price * qty
            order.total = total
            db.session.add(order)
            db.session.commit()
            session["cart"] = {}
            flash("¡Pedido realizado!", "success")
            return redirect(url_for("order_tracking", order_id=order.id))

        items, total = [], 0.0
        for pid, qty in cart.items():
            p = db.session.get(Product, int(pid))
            if not p:
                continue
            line_total = p.price * qty
            items.append({"product": p, "qty": qty, "line_total": line_total})
            total += line_total
        return render_template("checkout.html", items=items, total=total)

    @app.get("/orders/<int:order_id>")
    @login_required
    def order_tracking(order_id):
        order = db.session.get(Order, order_id)
        if not order or (not current_user.is_admin() and not current_user.is_employee() and order.user_id != current_user.id):
            abort(404)
        return render_template("order_tracking.html", order=order)

    # --- Empleado ---
    @app.get("/empleado/pedidos")
    @login_required
    def employee_orders():
        orders = Order.query.order_by(Order.created_at.asc()).all()
        return render_template("employee/orders.html", orders=orders)

    @app.post("/empleado/pedidos/<int:order_id>/avanzar")
    @login_required
    def employee_advance(order_id):
        order = db.session.get(Order, order_id)
        if not order:
            abort(404)
        next_map = {"pendiente": "preparando", "preparando": "listo", "listo": "entregado"}
        order.status = next_map.get(order.status, order.status)
        db.session.commit()
        flash("Pedido actualizado.", "success")
        return redirect(url_for("employee_orders"))

    @app.post("/empleado/pedidos/<int:order_id>/cancelar")
    @login_required
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
    
# --- Helpers seguros para plantillas ---
    @app.template_global()
    def safe_url_for(endpoint, **values):
        """Evita 500 si el endpoint no existe: devuelve '#'."""
        try:
            return url_for(endpoint, **values)
        except BuildError:
            return '#'

    @app.context_processor
    def inject_has_endpoint():
        """Permite preguntar en Jinja si un endpoint existe."""
        return {"has_endpoint": lambda name: name in app.view_functions}

# --- Endpoints mínimos de Admin (para que los links no rompan) ---
    @app.get("/admin")
    @login_required
    def admin_dashboard():
        total_sales = 0  # si aún no tenés ventas, ponelo en 0
        total_orders = Order.query.count() if 'Order' in globals() else 0
        products_count = Product.query.count()
        users_count = User.query.count()
        return render_template("admin/dashboard.html",
                            total_sales=total_sales,
                            total_orders=total_orders,
                            products_count=products_count,
                            users_count=users_count)

    

    @app.get("/admin/categorias")
    @login_required
    def admin_categories():
        categories = Category.query.order_by(Category.name.asc()).all()
        return render_template("admin/categories.html", categories=categories)
    
    @app.route("/admin/categorias/nueva", methods=["GET", "POST"])
    @login_required
    def admin_category_new():
        form = CategoryForm()
        if form.validate_on_submit():
            c = Category(name=form.name.data.strip())
            db.session.add(c)
            db.session.commit()
            flash("Categoría creada correctamente.", "success")
            return redirect(url_for("admin_categories"))
        return render_template("admin/category_form.html", form=form, action="Nueva")


    @app.route("/admin/categorias/<int:category_id>/editar", methods=["GET", "POST"])
    @login_required
    def admin_category_edit(category_id):
        c = Category.query.get_or_404(category_id)
        form = CategoryForm(obj=c)
        if form.validate_on_submit():
            c.name = form.name.data.strip()
            db.session.commit()
            flash("Categoría actualizada.", "success")
            return redirect(url_for("admin_categories"))
        return render_template("admin/category_form.html", form=form, action="Editar")


    @app.post("/admin/categorias/<int:category_id>/eliminar")
    @login_required
    def admin_category_delete(category_id):
        c = Category.query.get_or_404(category_id)
        db.session.delete(c)
        db.session.commit()
        flash("Categoría eliminada.", "info")
        return redirect(url_for("admin_categories"))
    
        # ------------------ ADMIN PRODUCTOS ------------------

    @app.route("/admin/productos")
    @login_required
    def admin_products():
        products = Product.query.order_by(Product.id.asc()).all()
        return render_template("admin/products.html", products=products)

    @app.route("/admin/productos/nuevo", methods=["GET", "POST"])
    @login_required
    def admin_product_new():
        form = ProductForm()
        if form.validate_on_submit():
            p = Product(
                name=form.name.data.strip(),
                price=form.price.data,
                stock=form.stock.data,
                category_id=form.category_id.data,
                is_active=form.is_active.data
        )

        # Imagen
            if form.image_url.data:
                p.image_url = form.image_url.data.filename
                image_path = os.path.join(app.static_folder, "images", form.image_url.data.filename)
                form.image_url.data.save(image_path)

            db.session.add(p)
            db.session.commit()
            flash("Producto agregado correctamente.", "success")
            return redirect(url_for("admin_products"))

        return render_template("admin/product_form.html", form=form, action="Nuevo")

    @app.route("/admin/productos/<int:product_id>/editar", methods=["GET", "POST"])
    @login_required
    def admin_product_edit(product_id):
        p = db.session.get(Product, product_id)
        if not p:
            abort(404)
        form = ProductForm(obj=p)

        if form.validate_on_submit():
            form.populate_obj(p)
            if form.image_url.data:
                p.image_url = form.image_url.data.filename
                image_path = os.path.join(app.static_folder, "images", form.image_url.data.filename)
                form.image_url.data.save(image_path)
            db.session.commit()
            flash("Producto actualizado.", "success")
            return redirect(url_for("admin_products"))

        return render_template("admin/product_form.html", form=form, action="Editar")

    @app.post("/admin/productos/<int:product_id>/eliminar")
    @login_required
    def admin_product_delete(product_id):
        p = db.session.get(Product, product_id)
        if not p:
            abort(404)
        db.session.delete(p)
        db.session.commit()
        flash("Producto eliminado.", "info")
        return redirect(url_for("admin_products"))


    return app


# --- Ejecutar servidor ---
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
