from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.user import User


class RegisterForm(FlaskForm):
    username = StringField('Usuario', validators=[
        DataRequired(message='El usuario es obligatorio.'),
        Length(min=3, max=64, message='Entre 3 y 64 caracteres.')
    ])
    email = StringField('Correo', validators=[
        DataRequired(message='El correo es obligatorio.'),
        Email(message='Correo no válido.')
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

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Ya existe una cuenta con ese correo.')


class LoginForm(FlaskForm):
    email = StringField('Correo', validators=[
        DataRequired(message='El correo es obligatorio.'),
        Email(message='Correo no válido.')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es obligatoria.')
    ])
    remember = BooleanField('Recordarme')
    submit = SubmitField('Entrar')
