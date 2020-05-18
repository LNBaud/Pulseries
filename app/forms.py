from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User


#Formulaire de connexion
class LoginForm(FlaskForm):
    username = StringField("Nom d'utilisateur", validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Connexion')


#Formulaire d'inscription
class RegistrationForm(FlaskForm):
    username = StringField("Nom d'utilisateur", validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    password2 = PasswordField('Confirmez le mot de passe', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Inscription')

    def validate_username(self, username):
        '''Vérifie que le nom d'utilisateur n'est pas déjà utilisé'''
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Veuillez utiliser un autre nom d'utilisateur.")

    def validate_email(self, email):
        '''Vérifie que le mail n'est pas déjà utilisé'''
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Veuillez utiliser une autre adresse email.")
