from app import create_app
from models import db, User, Category, Product, Role

app = create_app()

with app.app_context():
    # Create base roles users
    if not User.query.filter_by(email="admin@aroma.cl").first():
        admin = User(name="Admin", email="admin@aroma.cl", role=Role.ADMIN)
        admin.set_password("admin123")
        db.session.add(admin)
        print("Creado usuario admin: admin@aroma.cl / admin123")

    if not User.query.filter_by(email="empleado@aroma.cl").first():
        emp = User(name="Empleado", email="empleado@aroma.cl", role=Role.EMPLOYEE)
        emp.set_password("empleado123")
        db.session.add(emp)
        print("Creado usuario empleado: empleado@aroma.cl / empleado123")

    if not User.query.filter_by(email="cliente@aroma.cl").first():
        cli = User(name="Cliente Demo", email="cliente@aroma.cl", role=Role.CUSTOMER)
        cli.set_password("cliente123")
        db.session.add(cli)
        print("Creado cliente demo: cliente@aroma.cl / cliente123")

    # Categories
    bebidas = Category.query.filter_by(name="Bebidas").first() or Category(name="Bebidas")
    dulces = Category.query.filter_by(name="Dulces").first() or Category(name="Dulces")
    salados = Category.query.filter_by(name="Salados").first() or Category(name="Salados")
    db.session.add_all([bebidas, dulces, salados])

    db.session.commit()

    # Products (idempotent-ish)
    def ensure_product(name, price, stock, cat, image_url, desc):
        p = Product.query.filter_by(name=name).first()
        if not p:
            p = Product(name=name, price=price, stock=stock, category_id=cat.id,
                        image_url=image_url, description=desc)
            db.session.add(p)

    ensure_product("Café Americano", 1900, 20, bebidas,
    "https://images.unsplash.com/photo-1509042239860-f550ce710b93?q=80&w=800&auto=format&fit=crop",
    "Café negro intenso."
)


    ensure_product("Capuchino", 2400, 15, bebidas,
                   "https://images.unsplash.com/photo-1511920170033-f8396924c348?q=80&w=800&auto=format&fit=crop",
                   "Espuma cremosa con leche.")

    ensure_product("Muffin de Chocolate", 1500, 25, dulces,
                   "https://images.unsplash.com/photo-1499636136210-6f4ee915583e?q=80&w=800&auto=format&fit=crop",
                   "Muffin casero con chips de chocolate.")

    ensure_product("Sandwich Jamón Queso",2100, 18, salados,
                  "https://images.unsplash.com/photo-1606755962773-0e48ab944d2d?q=80&w=800&auto=format&fit=crop",
                  "Sandwich tostado clásico de jamón y queso."
)


    db.session.commit()
    print("Datos de ejemplo cargados.")