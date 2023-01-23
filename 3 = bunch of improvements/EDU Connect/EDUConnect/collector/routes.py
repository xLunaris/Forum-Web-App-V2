from flask import (render_template, request, Blueprint, session)
from EDUConnect.models import Post, Comment
from wordcloud import WordCloud
import base64
import joblib
import os
import io
from PIL import Image

collector = Blueprint('collector', __name__)

def generate_wordcloud(comments_text):
    wordcloud = WordCloud().generate(comments_text)
    return wordcloud

@collector.route('/comments/<int:post_id>', methods=['GET','POST'])
def comments(post_id):
    post_title = ""
    comments = []
    post = Post.query.get(post_id)
    post_title = post.title
    page = request.args.get('page', 1, type=int)
    comments = Comment.query.filter_by(post_id=post_id).paginate(page=page, per_page=4)
        # load the pre-trained model
    model = joblib.load(os.path.join(os.getcwd(), "EDUConnect", "collector", "SVMMODEL_OVERSAMPLING.joblib"))
        # classify the comments
    for comment in comments:
        prediction = model.predict([comment.text])
        comment.sentiment = prediction
    total_comments = len(comments.items)
    total_positive = sum(1 for comment in comments.items if comment.sentiment == "Positive")
    total_negative = sum(1 for comment in comments.items if comment.sentiment == 'Negative')
    total_neutral = sum(1 for comment in comments.items if comment.sentiment == 'Neutral')
    total_very_positive = sum(1 for comment in comments.items if comment.sentiment == "Very Positive")
    total_very_negative = sum(1 for comment in comments.items if comment.sentiment == "Very Negative")

    comments_for_wordcloud = Comment.query.filter_by(post_id=post_id)
    comments_text = " ".join([comment.text for comment in comments_for_wordcloud])
    wordcloud = generate_wordcloud(comments_text)
    img = io.BytesIO()
    wordcloud.to_image().save(img, format='PNG')
    img.seek(0)
    wordcloud_encoded = base64.b64encode(img.getvalue()).decode('utf-8')
    return render_template('comments.html', comments=comments, post_title=post_title, post_id=post_id, 
                            total_comments=total_comments, total_positive=total_positive, total_very_positive=total_very_positive, 
                            total_very_negative=total_very_negative, total_negative=total_negative, total_neutral=total_neutral, 
                            wordcloud=wordcloud_encoded)






