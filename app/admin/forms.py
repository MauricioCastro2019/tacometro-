from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, BooleanField, SelectMultipleField, SubmitField
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
    image_file = FileField('Subir imagen', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Solo imágenes JPG, PNG o WebP.')
    ])
    category_ids = SelectMultipleField(
        'Tipos de taco',
        coerce=int,
        validators=[DataRequired(message='Selecciona al menos un tipo de taco.')]
    )
    is_active = BooleanField('Activa', default=True)
    submit = SubmitField('Guardar')


class ImportForm(FlaskForm):
    file = FileField('Archivo (.xlsx o .csv)', validators=[
        FileRequired(message='Selecciona un archivo.'),
        FileAllowed(['xlsx', 'csv'], 'Solo se permiten archivos .xlsx o .csv.')
    ])
    submit = SubmitField('Importar taquerías')
