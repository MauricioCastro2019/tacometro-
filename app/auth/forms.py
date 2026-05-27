from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp, ValidationError
from app.models.user import User


class RegisterForm(FlaskForm):
    username = StringField('Usuario', validators=[
        DataRequired(message='El usuario es obligatorio.'),
        Length(min=3, max=64, message='Entre 3 y 64 caracteres.')
    ])
    phone = StringField('Teléfono', validators=[
        DataRequired(message='El teléfono es obligatorio.'),
        Regexp(r'^\d{10}$', message='Ingresa 10 dígitos numéricos (sin espacios ni guiones).')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es obligatoria.'),
        Length(min=6, message='Mínimo 6 caracteres.')
    ])
    password2 = PasswordField('Confirmar contraseña', validators=[
        DataRequired(),
        EqualTo('password', message='Las contraseñas no coinciden.')
    ])
    submit = SubmitField('Registrarme')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Ese nombre de usuario ya está en uso.')

    def validate_phone(self, field):
        if User.query.filter_by(phone=field.data).first():
            raise ValidationError('Ya existe una cuenta con ese número.')


class LoginForm(FlaskForm):
    phone = StringField('Teléfono', validators=[
        DataRequired(message='El teléfono es obligatorio.'),
        Regexp(r'^\d{10}$', message='Ingresa 10 dígitos numéricos.')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es obligatoria.')
    ])
    remember = BooleanField('Recordarme')
    submit = SubmitField('Entrar')
