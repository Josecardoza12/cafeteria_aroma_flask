from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Contraseña", validators=[DataRequired()])
    submit = SubmitField("Ingresar")

class RegisterForm(FlaskForm):
    name = StringField("Nombre", validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Crear cuenta")

class ProductForm(FlaskForm):
    name = StringField("Nombre", validators=[DataRequired(), Length(min=2, max=180)])
    description = TextAreaField("Descripción", validators=[Optional()])
    price = FloatField("Precio", validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField("Stock", validators=[DataRequired(), NumberRange(min=0)])
    category_id = SelectField("Categoría", coerce=int, validators=[Optional()])
    image_url = StringField("URL de imagen", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Guardar")

class CategoryForm(FlaskForm):
    name = StringField("Nombre", validators=[DataRequired(), Length(min=2, max=120)])
    submit = SubmitField("Guardar")