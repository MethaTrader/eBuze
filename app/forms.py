from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional

COUNTRY_CHOICES = [
    ('USA', 'United States'),
    ('UK', 'United Kingdom'),
    ('Canada', 'Canada'),
    ('Australia', 'Australia'),
    ('Germany', 'Germany'),
    ('France', 'France'),
    ('Spain', 'Spain'),
    ('Italy', 'Italy'),
    ('Russia', 'Russia (Latin)'),
    ('China', 'China'),
    ('Japan', 'Japan'),
    ('South Korea', 'South Korea'),
    ('Brazil', 'Brazil'),
    ('Mexico', 'Mexico'),
    ('India', 'India'),
    ('Slovakia', 'Slovakia'),
    ('Czech Republic', 'Czech Republic'),
    ('Georgia', 'Georgia'),
    ('Bulgaria', 'Bulgaria')
]

class EmailAccountForm(FlaskForm):
    first_name = StringField('First Name', validators=[Length(max=64)])
    last_name = StringField('Last Name', validators=[Length(max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=120)])
    country = SelectField('Country', choices=COUNTRY_CHOICES, validators=[DataRequired()])
    generate_name = BooleanField('Generate Random Name')
    submit = SubmitField('Create Email Account')

class MexcAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=64)])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=120)])
    email_id = SelectField('Email Account', coerce=int, validators=[DataRequired()])
    referrer_id = SelectField('Referrer', coerce=int, validators=[Optional()])
    proxy = StringField('Proxy', validators=[Optional(), Length(max=120)])
    referral_link = StringField('Referral Link', validators=[Optional(), Length(max=255)])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
    volume_completed = BooleanField('$100 Volume Completed')
    submit = SubmitField('Create MEXC Account')