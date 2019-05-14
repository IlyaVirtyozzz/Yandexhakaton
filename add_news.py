from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class AddNewsForm(FlaskForm):
    task = StringField('Задача', validators=[DataRequired()])
    content = TextAreaField('Код', validators=[DataRequired()])
    submit = SubmitField('Добавить')
