from models import db, Role, User, Category, Product
from werkzeug.security import generate_password_hash

def seed_db():
    # Evitar duplicar datos si ya existen
    if Role.query.first():
        print(">>> Seed ya ejecutado, se omite.")
        return

    # ----- Roles -----
    admin_role = Role(name="admin")
    employee_role = Role(name="employee")
    customer_role = Role(name="customer")
    db.session.add_all([admin_role, employee_role, customer_role])
    db.session.commit()
    print(">>> Roles creados")

    # ----- Usuarios -----
    admin = User(
        name="Administrador General",
        email="admin@aroma.cl",
        password_hash=generate_password_hash("admin123"),
        role_id=admin_role.id
    )

    empleado = User(
        name="Empleado Cafetería",
        email="empleado@aroma.cl",
        password_hash=generate_password_hash("empleado123"),
        role_id=employee_role.id
    )

    cliente = User(
        name="Cliente Prueba",
        email="cliente@aroma.cl",
        password_hash=generate_password_hash("cliente123"),
        role_id=customer_role.id
    )

    db.session.add_all([admin, empleado, cliente])
    db.session.commit()
    print(">>> Usuarios creados")

    # ----- Categorías -----
    cafes = Category(name="Cafés")
    frias = Category(name="Bebidas frías")
    postres = Category(name="Postres")
    db.session.add_all([cafes, frias, postres])
    db.session.commit()
    print(">>> Categorías creadas")

    # ----- Productos -----
    productos = [
        Product(name="Capuccino Italiano", description="Espresso con leche espumada", price=2500, stock=20, image_url="/static/images/capuccino.jpg", category_id=cafes.id, is_active=True),
        Product(name="Latte Vainilla", description="Café suave con esencia de vainilla natural", price=2800, stock=15, image_url="/static/images/latte_vainilla.jpg", category_id=cafes.id, is_active=True),
        Product(name="Mocaccino", description="Café con chocolate y crema batida", price=2900, stock=12, image_url="/static/images/mocaccino.jpg", category_id=cafes.id, is_active=True),
        Product(name="Iced Coffee", description="Café frío con hielo y esencia de vainilla", price=2700, stock=10, image_url="/static/images/iced_coffee.jpg", category_id=frias.id, is_active=True),
        Product(name="Brownie", description="Brownie casero de chocolate belga", price=2200, stock=25, image_url="/static/images/brownie.jpg", category_id=postres.id, is_active=True),
        Product(name="Cheesecake Frutilla", description="Cheesecake artesanal con salsa de frutilla", price=3200, stock=10, image_url="/static/images/cheesecake.jpg", category_id=postres.id, is_active=True),
    ]

    db.session.add_all(productos)
    db.session.commit()
    print(">>> Productos creados correctamente")

    print("✅ Base de datos inicializada correctamente.")
