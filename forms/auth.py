from flask_wtf.form import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length


class AuthForm(FlaskForm):
    username = StringField(validators=[DataRequired(), Length(min=1, max=100)])
    password = PasswordField(validators=[DataRequired(), Length(min=1, max=100)])
