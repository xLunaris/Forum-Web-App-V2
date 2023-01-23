from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from EDUConnect.models import Announcement
from EDUConnect import db 
from EDUConnect.announcements.forms import AnnouncementForm

announcements = Blueprint('announcements', __name__)

@announcements.route("/announcements", methods=["GET", "POST"])
def all_announcements():
    announcements = Announcement.query.all()
    return render_template('layout.html', announcements=announcements)


@announcements.route("/announcement/new", methods=['GET', 'POST'])
@login_required
def new_announcement():
    form = AnnouncementForm(request.form)
    if form.validate_on_submit():
        announcement = Announcement(title=form.title.data, content=form.content.data, author_id=current_user.id)
        db.session.add(announcement)
        db.session.commit()
        flash('Your announcement has been created!', 'success')
        return redirect(url_for('announcements.all_announcements'))
    return render_template('create_announcement.html', title='New Announcement', form=form, legend='New Announcement')

@announcements.route("/announcement/<int:announcement_id>", methods=["GET", "POST"])
def announcement(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    return render_template('announcement.html', title=announcement.title, announcement=announcement, author=announcement.author.username)

