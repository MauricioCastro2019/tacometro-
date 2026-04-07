from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, URL


class PlaceForm(FlaskForm):
    name = StringField('Nombre', validators=[
        DataRequired(message='El nombre es obligatorio.'),
        Length(max=128)
    ])
    description = TextAreaField('Descripción', validators=[Optional(), Length(max=1000)])
    address = StringField('Dirección', validators=[Optional(), Length(max=256)])
    city = StringField('Ciudad', validators=[DataRequired()], default='León')
    state = StringField('Estado', validators=[DataRequired()], default='Guanajuato')
    phone = StringField('Teléfono', validators=[Optional(), Length(max=20)])
    image_url = StringField('URL de imagen', validators=[Optional(), URL(message='URL no válida.')])
    category_id = SelectField('Categoría', coerce=int, validators=[DataRequired()])
    is_active = BooleanField('Activa', default=True)
    submit = SubmitField('Guardar')
