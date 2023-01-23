from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from EDUConnect import db
from EDUConnect.models import Post, Comment, User
from EDUConnect.posts.forms import PostForm
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

posts = Blueprint('posts', __name__)


@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm(request.form)
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user, anonymous_comments=form.anonymous_comments.data, is_private=form.is_private.data)
        if form.is_private.data:
            access_key = request.form.get("access_key")
            if access_key:
                hashed_key = bcrypt.generate_password_hash(access_key).decode("utf-8")
                post.access_key = hashed_key
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')


@posts.route("/post/<int:post_id>", methods=["GET", "POST"])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id).all()

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
    else:
        return render_template('post.html', title=post.title, post=post, comments=comments, user=current_user)


@posts.route("/comment/<int:post_id>", methods=["POST"])
def comment(post_id):
    post = Post.query.get(post_id)
    # code to handle creating new comment
    comments = Comment.query.join(User, User.id == Comment.author).filter_by(post_id=post_id).all()
    return render_template('post.html', title=post.title, post=post, comments=comments)

@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    # Delete all comments associated with the post
    Comment.query.filter_by(post_id=post_id).delete()
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))



#for creating comments on post

@posts.route("/create-comment/<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')

    if not text:
        flash('Comment cannot be empty.', category='error')
    else:
        post = Post.query.filter_by(id=post_id).first()
        if post:
            comment = Comment(text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exist.', category='error')

    return redirect(url_for('posts.post', post_id=post_id))


@posts.route("/delete-comment/<comment_id>", methods=["POST"])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash('Comment does not exist.', category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You do not have permission to delete this comment.', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('posts.post', post_id=comment.post_id))
