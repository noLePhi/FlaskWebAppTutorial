from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import Post, User, Comment, Like
from . import db

resources = Blueprint("resources", __name__)

@resources.route("/")
@resources.route("/resources/books", methods=['GET', 'POST'])
@login_required
def books():
    return render_template("resources_books.html", user=current_user)

@resources.route("/resources/courses", methods=['GET', 'POST'])
@login_required
def courses():
    return render_template("resources_courses.html", user=current_user)

@resources.route("/resources/yt", methods=['GET', 'POST'])
@login_required
def youtube():
    return render_template("resources_yt.html", user=current_user)

@resources.route("/resources/github", methods=['GET', 'POST'])
@login_required
def github():
    return render_template("resources_github.html", user=current_user)

@resources.route("/resources/blogs", methods=['GET', 'POST'])
@login_required
def blogs():
    return render_template("resources_blogs.html", user=current_user)