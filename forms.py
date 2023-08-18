from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, BooleanField, DecimalField, DateField, SelectField
from wtforms.validators import DataRequired, NumberRange
from datetime import date

distances = [10, 18, 20, 30, 40, 50, 60, 70, 80, 90, 100, ]

# 1.09361 = yard --> metre conversion

class GetScoreData(FlaskForm):
    season = SelectField("Season: ", choices=[("outdoors", "Outdoor"), ("indoors", "Indoor")], validators=[DataRequired()], default=0)
    distance = SelectField("Distance", choices=distances, validators=[DataRequired()])
    units = SelectField("Units: ", choices=[(1, "yds"), (1.09361, "m")], validators=[DataRequired()], default=1)
    days_till = DateField("Date: ", validators=[DataRequired()], default=date.today())
    is_comp = BooleanField("Competition? ")
    submit = SubmitField("Submit")
    
class GetNewScore(FlaskForm):
    season = SelectField("Season: ", choices=[("outdoors", "Outdoor"), ("indoors", "Indoor")], validators=[DataRequired()], default=0)
    arrow_average = DecimalField("Average Arrow Score: ", validators=[DataRequired(), NumberRange(max=10)])
    distance = SelectField("Distance", choices=distances, validators=[DataRequired()], default=10)
    units = SelectField("Units: ", choices=[(1, "yds"), (1.09361, "m")], validators=[DataRequired()], default=1)
    date = DateField("Date: ", validators=[DataRequired()], default=date.today())
    golds = IntegerField("Golds: ", validators=[DataRequired()])
    total_arrows = IntegerField("Number of arrows: ", validators=[DataRequired()])
    is_comp = SelectField("Competition?", choices=[(1, "Yes"), (0, "No")], default=0)
    submit = SubmitField("Submit")