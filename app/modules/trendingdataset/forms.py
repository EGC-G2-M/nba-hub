from flask_wtf import FlaskForm
from wtforms import SubmitField


class TrendingdatasetForm(FlaskForm):
    submit = SubmitField('Save trendingdataset')
