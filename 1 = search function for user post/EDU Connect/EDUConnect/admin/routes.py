from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from EDUConnect import db
from EDUConnect.models import Post, Comment, User
from flask_bcrypt import generate_password_hash, check_password_hash


admin = Blueprint('admin', __name__)

@admin.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        abort(403)
    else:
        # code for displaying the admin dashboard goes here
        # For example, you can query the database to get the number of total posts, total users, etc. and pass it to the template
        total_posts = Post.query.count()
        total_users = User.query.count()
        total_comments = Comment.query.count()

        return render_template("admin_dashboard.html", total_posts=total_posts, total_users=total_users, total_comments=total_comments)

from flask_bcrypt import generate_password_hash, check_password_hash

@admin.route("/admin/create_special_user", methods=['GET','POST'])
@login_required
def create_special_user():
    if current_user.role != "admin":
        abort(403)
    else: 
        if request.method == 'POST':
            # get form data
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            role = request.form.get('role') 
            # validate form data
            if not username or not email or not password or not role:
                flash('Please enter all fields', 'danger')
                return redirect(url_for('admin.create_special_user'))
            # check if email already exists
            user = User.query.filter_by(email=email).first()
            if user:
                flash('Email already exists', 'danger')
                return redirect(url_for('admin.create_special_user'))
            # create new user object
            hashed_password = generate_password_hash(password).decode('utf-8')
            new_user = User(username=username, email=email, password=hashed_password, role=role)
            db.session.add(new_user)
            db.session.commit()
            flash('User Account Created!', 'success')
            return redirect(url_for('admin.admin_dashboard'))
    return render_template("create_special_user.html")



@admin.route('/comments')
def comments():
    page = request.args.get('page', 1, type=int)
    comments = Comment.query.paginate(page=page, per_page=5)
    return render_template('admin_comments.html', comments=comments)

@admin.route('/posts')
def posts():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.paginate(page=page, per_page=5)
    return render_template('admin_posts.html', posts=posts)

@admin.route('/users')
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=5)
    return render_template('admin_users.html', users=users)
 

@admin.route("/delete_post/<int:post_id>", methods=['GET', 'POST'])
def delete_post(post_id):
    if current_user.role != "admin":
        abort(403)
    else:
        post = Post.query.get_or_404(post_id)
        Comment.query.filter_by(post_id=post_id).delete()
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted!', 'success')
        return redirect(url_for('admin.posts'))

@admin.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    if request.method == 'POST':
        user = User.query.get(user_id)
        if user:
            # Delete all comments on posts where the author is the deleted user
            comments_on_deleted_user_posts = Comment.query.filter(
                Comment.post.has(author=user)
            ).all()
            for comment in comments_on_deleted_user_posts:
                db.session.delete(comment)
            # Delete the user's posts and comments
            db.session.query(Post).filter_by(author=user).delete()
            db.session.query(Comment).filter_by(user=user).delete()
            # Delete the user
            db.session.delete(user)
            db.session.commit()
            flash('User has been deleted.', 'success')
            return redirect(url_for('admin.users'))
        else:
            flash('User not found.', 'danger')
            return redirect(url_for('admin.users'))
    else:
        return redirect(url_for('admin.users'))



