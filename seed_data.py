# seed_data.py
from models import db, User, Category, Product, Role
from werkzeug.security import generate_password_hash

def seed_db():
    try:
        print(">>> Ejecutando seed_db...")

        # Usuarios (solo si no hay)
        if not User.query.first():
            admin = User(
                name="Administrador General",
                email="admin@aroma.cl",
                password_hash=generate_password_hash("admin123"),
                role=Role.ADMIN
            )
            empleado = User(
                name="Empleado Cafetería",
                email="empleado@aroma.cl",
                password_hash=generate_password_hash("empleado123"),
                role=Role.EMPLOYEE
            )
            cliente = User(
                name="Cliente Prueba",
                email="cliente@aroma.cl",
                password_hash=generate_password_hash("cliente123"),
                role=Role.CUSTOMER
            )
            db.session.add_all([admin, empleado, cliente])
            db.session.commit()
            print(">>> Usuarios creados")

        # Categorías
        if not Category.query.first():
            cafes = Category(name="Cafés")
            frias = Category(name="Bebidas frías")
            postres = Category(name="Postres")
            salados = Category(name="Snacks salados")
            db.session.add_all([cafes, frias, postres, salados])
            db.session.commit()
            print(">>> Categorías creadas")
        else:
            cafes = Category.query.filter_by(name="Cafés").first()
            frias = Category.query.filter_by(name="Bebidas frías").first()
            postres = Category.query.filter_by(name="Postres").first()
            salados = Category.query.filter_by(name="Snacks salados").first()

        # Productos con imagen (solo si no hay)
        if not Product.query.first():
            productos = [
                Product(name="Capuccino Italiano", description="Espresso con leche espumada",
                        price=2500, stock=20, image_url="capuccino.jpg", category=cafes, is_active=True),
                Product(name="Latte Vainilla", description="Café suave con esencia de vainilla natural",
                        price=2800, stock=15, image_url="latte.jpg", category=cafes, is_active=True),
                Product(name="Frappe Moka", description="Café frío con chocolate",
                        price=3200, stock=18, image_url="frappe_moka.jpg", category=frias, is_active=True),
                Product(name="Té Matcha", description="Matcha latte",
                        price=3000, stock=10, image_url="te_matcha.jpg", category=frias, is_active=True),
                Product(name="Brownie", description="Brownie casero de chocolate",
                        price=2200, stock=25, image_url="brownie.jpg", category=postres, is_active=True),
                Product(name="Cheesecake Frutilla", description="Cheesecake artesanal",
                        price=2600, stock=20, image_url="cheesecake.jpg", category=postres, is_active=True),
                Product(name="Galletas Caseras", description="Mantequilla y chips de chocolate",
                        price=1500, stock=40, image_url="galletas.jpg", category=postres, is_active=True),
                Product(name="Sándwich de Pollo", description="Ciabatta, pollo y palta",
                        price=3500, stock=12, image_url="sandwich_pollo.jpg", category=salados, is_active=True),
                Product(name="Muffin de Chocolate", description="Muffin con chips de chocolate",
                        price=1800, stock=30, image_url="muffin_choco.jpg", category=postres, is_active=True),
                Product(name="Medialuna", description="Croissant argentino",
                        price=1200, stock=50, image_url="medialuna.jpg", category=salados, is_active=True),
            ]
            db.session.add_all(productos)
            db.session.commit()
            print(">>> Productos creados ✅")

        print(">>> seed_db listo")
    except Exception as e:
        db.session.rollback()
        print("❌ Error en seed_db:", e)
