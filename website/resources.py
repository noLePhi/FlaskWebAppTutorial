from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import Post, User, Comment, Like
from . import db

resources = Blueprint("resources", __name__)

@resources.route("/")
@resources.route("/resources", methods=['GET', 'POST'])
@login_required
def last_articles():
    return render_template("resources.html", user=current_user)