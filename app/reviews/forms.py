from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, IntegerField, HiddenField
from wtforms.validators import DataRequired, NumberRange, Optional


class ReviewForm(FlaskForm):
    place_id = HiddenField(validators=[DataRequired()])

    taste_score    = IntegerField('Sabor',          validators=[DataRequired(), NumberRange(1, 10)])
    meat_score     = IntegerField('Carne',          validators=[DataRequired(), NumberRange(1, 10)])
    sauce_score    = IntegerField('Salsa',          validators=[DataRequired(), NumberRange(1, 10)])
    tortilla_score = IntegerField('Tortilla',       validators=[DataRequired(), NumberRange(1, 10)])
    value_score    = IntegerField('Precio-calidad', validators=[DataRequired(), NumberRange(1, 10)])
    hygiene_score  = IntegerField('Higiene',        validators=[DataRequired(), NumberRange(1, 10)])

    comment = TextAreaField('Comentario (opcional)', validators=[Optional()])
    submit  = SubmitField('Publicar reseña')
