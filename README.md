# Cafetería Aroma — Flask

Proyecto funcional con roles **Administrador**, **Empleado** y **Cliente**.
Incluye: autenticación, catálogo, carrito, checkout, seguimiento de pedidos,
panel de empleado para avanzar estados y panel admin con CRUD de productos y categorías.

## Requisitos
- Python 3.10+
- pip
- (opcional) virtualenv

## Instalación
```bash
cd cafeteria_aroma_flask
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

## Inicializar datos
```bash
# crea base de datos y usuarios demo
python seed.py
```

Usuarios de prueba:
- Admin: `admin@aroma.cl` / `admin123`
- Empleado: `empleado@aroma.cl` / `empleado123`
- Cliente: `cliente@aroma.cl` / `cliente123`

## Ejecutar
```bash
python app.py
# abrir http://127.0.0.1:5000
```

## Cómo se conecta HTML con Python (Flask + Jinja)
- En `app.py` definimos rutas (funciones) que retornan `render_template(...)`.
- En `/templates/*.html` usamos **Jinja2** (`{{ }}` y `{% %}`) para mostrar datos del backend.
- Los formularios usan **Flask-WTF** para validación y **CSRF**.
- Los clicks "Agregar al carrito" llaman a endpoints (`/cart/add/<id>`) que responden JSON y actualizan la UI.

## Estructura
```text
app.py                # rutas y app
models.py             # modelos SQLAlchemy
forms.py              # formularios WTForms
config.py             # configuración (SQLite)
seed.py               # datos demo
templates/            # vistas HTML (Jinja + Bootstrap 5)
static/css, static/js # estilos y scripts
```

## Personalización UI
- Edita `static/css/styles.css` (colores cálidos tipo cafetería).
- Cambia logos y textos en `templates/base.html` e `index.html`.
- Agrega imágenes a productos via campo "URL de imagen" en Admin.

## Notas
- El pago es simulado (efectivo/tarjeta). Para pasarela real, integrar SDK externo.
- Estados de pedido: `pendiente -> preparando -> listo -> entregado` (o `cancelado`).