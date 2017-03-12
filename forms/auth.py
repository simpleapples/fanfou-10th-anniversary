from flask_wtf.form import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Email, DataRequired, Length


class AuthForm(FlaskForm):
    email = StringField(validators=[DataRequired(), Email()])
    password = PasswordField(validators=[DataRequired(), Length(min=1, max=100)])
