from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Optional

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    is_private = BooleanField('Make this post private')
    anonymous_comments = BooleanField('Allow anonymous comments', validators=[Optional()])
    submit = SubmitField('Post')

