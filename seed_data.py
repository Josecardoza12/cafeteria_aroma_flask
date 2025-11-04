from models import db, Role, User, Category, Product
from werkzeug.security import generate_password_hash

def seed_db():
    """Inicializa la base de datos con roles, usuarios, categorías y productos"""
    try:
        # Verificar si ya se insertaron roles
        if db.session.query(Role).first():
            print(">>> Seed ya ejecutado, se omite.")
            return

        # -------- Crear Roles --------
        admin_role = Role(name="admin")
        employee_role = Role(name="employee")
        customer_role = Role(name="customer")
        db.session.add_all([admin_role, employee_role, customer_role])
        db.session.commit()
        print(">>> Roles creados correctamente")

        # -------- Crear Usuarios --------
        admin = User(
            name="Administrador General",
            email="admin@aroma.cl",
            password_hash=generate_password_hash("admin123"),
            role_id=admin_role.id,
        )
        empleado = User(
            name="Empleado Cafetería",
            email="empleado@aroma.cl",
            password_hash=generate_password_hash("empleado123"),
            role_id=employee_role.id,
        )
        cliente = User(
            name="Cliente Prueba",
            email="cliente@aroma.cl",
            password_hash=generate_password_hash("cliente123"),
            role_id=customer_role.id,
        )
        db.session.add_all([admin, empleado, cliente])
        db.session.commit()
        print(">>> Usuarios creados correctamente")

        # -------- Crear Categorías --------
        cafes = Category(name="Cafés")
        frias = Category(name="Bebidas frías")
        postres = Category(name="Postres")
        db.session.add_all([cafes, frias, postres])
        db.session.commit()
        print(">>> Categorías creadas correctamente")

        # -------- Crear Productos --------
        productos = [
            Product(name="Capuccino Italiano", description="Espresso con leche espumada", price=2500, stock=20, category_id=cafes.id, is_active=True),
            Product(name="Latte Vainilla", description="Café suave con esencia de vainilla natural", price=2800, stock=15, category_id=cafes.id, is_active=True),
            Product(name="Brownie", description="Brownie casero de chocolate belga", price=2200, stock=25, category_id=postres.id, is_active=True),
        ]
        db.session.add_all(productos)
        db.session.commit()
        print(">>> Productos creados correctamente ✅")

    except Exception as e:
        db.session.rollback()
        print("❌ Error durante seed_db:", e)
