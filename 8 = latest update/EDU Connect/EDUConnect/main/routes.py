from flask import render_template, request, Blueprint, redirect, url_for
from flask_login import current_user
from EDUConnect.models import Post, Announcement, User, Comment
from flask import flash
import bcrypt

main = Blueprint('main', __name__)

# This function displays all the post, announcement, and keyword search results on home.html
@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    announcements = Announcement.query.all()
    q = request.args.get('q')
    if q:
        posts = Post.query.filter((Post.title.contains(q) | Post.content.contains(q)) | User.username.contains(q)).join(User).order_by(Post.date_posted.desc()).paginate(page=page, per_page=4)
        if len(posts.items) == 0:
            flash('No post found', 'danger')
            return redirect(url_for('main.home'))
    else:
        posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=4)
    return render_template('home.html', posts=posts, announcements=announcements)

# This function displays search result for post_id input, but the function will check the post firs if its on private mode
@main.route("/post_id")
def post_id():
    announcements = Announcement.query.all()
    post_id = request.args.get('postid')
    post = Post.query.get(post_id)
    comments = Comment.query.filter_by(post_id=post_id).all()
    
    if post:
        if post.is_private:
            if current_user == post.author:
                return render_template('post.html', title=post.title, post=post, comments=comments, user=current_user)
            else:
                if request.method == "POST":
                    input_key = request.form.get("access_key")
                    if bcrypt.check_password_hash(post.access_key, input_key):
                        return render_template('post.html', title=post.title, post=post, comments=comments, user=current_user)
                    else:
                        flash("Access key is incorrect.", "danger")
                        return redirect(url_for("posts.post", post_id=post_id))
                else:
                    return render_template("access_key.html", post=post)
        return render_template('post.html', post=post, announcements=announcements, comments=comments, user=current_user)
    else: 
        flash('No post found', 'danger')
        return redirect(url_for('main.home'))

# this function redirects user to about page
@main.route("/about")
def about():
    return render_template('about.html', title='About')