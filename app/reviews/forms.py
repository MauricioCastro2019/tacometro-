from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import TextAreaField, SubmitField, IntegerField, HiddenField, StringField
from wtforms.validators import DataRequired, NumberRange, Optional, Length


class ReviewForm(FlaskForm):
    place_id = HiddenField(validators=[DataRequired()])
    nickname = StringField('Tu nombre o apodo', validators=[Optional(), Length(max=64)])

    sabor = IntegerField('Sabor', validators=[DataRequired(), NumberRange(1, 5)])
    salsa = IntegerField('Salsa', validators=[DataRequired(), NumberRange(1, 5)])
    servicio = IntegerField('Servicio', validators=[DataRequired(), NumberRange(1, 5)])
    precio_calidad = IntegerField('Precio/calidad', validators=[DataRequired(), NumberRange(1, 5)])
    higiene = IntegerField('Higiene/lugar', validators=[DataRequired(), NumberRange(1, 5)])

    comentario = TextAreaField('Comentario (opcional)', validators=[Optional()])
    foto_comida = FileField('Foto de comida', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Solo imágenes JPG, PNG o WebP.')
    ])

    submit = SubmitField('Guardar calificación')
