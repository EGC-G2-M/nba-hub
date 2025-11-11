from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Length


class CommentForm(FlaskForm):
    content = TextAreaField(
        "Comment", 
        validators=[
            DataRequired(message="The comment cannot be empty."), 
            Length(min=1, max=1000, message="The comment must be between 1 and 1000 characters.")
        ]
    )
    
    dataset_id = HiddenField("Dataset ID", validators=[DataRequired(message="Dataset ID is missing.")]) 
    
    parent_id = HiddenField("Parent Comment ID") 
    
    submit = SubmitField("Post Comment")