from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import Post, User, Comment, Like
from . import db
from bs4 import BeautifulSoup
import requests
import os
import json
import lxml


views = Blueprint("views", __name__)


@views.route("/")
@views.route("/home")
def home():
    return render_template("home.html", user=current_user)

@views.route("/author")
@login_required
def author():
    return render_template("author.html", user=current_user)

@views.route("/articles", methods=['GET', 'POST'])
@login_required
def get_articles():
    headers = {
        'User-agent':
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
    }

    proxies = {
        'http': os.getenv('HTTP_PROXY')  # or just type proxy here without os.getenv()
    }

    research_subject = "deep learning"

    page_url = 'https://scholar.google.com/scholar?hl=fr&as_sdt=0,5&q=%22' + research_subject + '%22&scisbd=1'

    html = requests.get(page_url, headers=headers, proxies=proxies).text

    soup = BeautifulSoup(html, 'lxml')

    # Scrape just PDF links
    for pdf_link in soup.select('.gs_or_ggsm a'):
        pdf_file_link = pdf_link['href']
        print(pdf_file_link)

    data =[]

    for result in soup.select('.gs_ri'):
        title = result.select_one('.gs_rt').text
        title_link = result.select_one('.gs_rt a')['href']
        publication_info = result.select_one('.gs_a').text
        snippet = result.select_one('.gs_rs').text
        cited_by = result.select_one('#gs_res_ccl_mid .gs_nph+ a')['href']
        related_articles = result.select_one('a:nth-child(4)')['href']
        try:
            all_article_versions = result.select_one('a~ a+ .gs_nph')['href']
        except:
            all_article_versions = None

        data.append({
            'title': title,
            'title_link': title_link,
            'publication_info': publication_info,
            'snippet': snippet,
            'cited_by': f'https://scholar.google.com{cited_by}',
            'related_articles': f'https://scholar.google.com{related_articles}',
            'all_article_versions': f'https://scholar.google.com{all_article_versions}',
        })

    print(json.dumps(data, indent=2, ensure_ascii=False))

    return render_template('articles.html', user=current_user, articles=data)

@views.route("/posts", methods=['GET', 'POST'])
@login_required
def get_posts():
    posts = Post.query.all()
    return render_template('posts.html', user=current_user, posts=posts)

@views.route("/create_post", methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == "POST":
        text = request.form.get('text')

        if not text:
            flash('Post cannot be empty', category='error')
        else:
            post = Post(text=text, author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
            posts = Post.query.all()
            return render_template('posts.html', user=current_user, posts=posts)

    return render_template('create_post.html', user=current_user)


@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("Post does not exist.", category='error')
    elif current_user.id != post.author:
        flash('You do not have permission to delete this post.', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', category='success')

    posts = Post.query.all()
    return render_template('posts.html', user=current_user, posts=posts)


# check all posts of a specific user
@views.route("/posts/<username>")
@login_required
def posts(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('No user with that username exists.', category='error')
        posts = Post.query.all()
        return render_template('posts.html', user=current_user, posts=posts)

    posts = user.posts
    return render_template("userposts.html", user=current_user, posts=posts, username=username)


@views.route("/create-comment/<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')

    if not text:
        flash('Comment cannot be empty.', category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(
                text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exist.', category='error')

    posts = Post.query.all()
    return render_template('posts.html', user=current_user, posts=posts)


@views.route("/delete-comment/<comment_id>")
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

    posts = Post.query.all()
    return render_template('posts.html', user=current_user, posts=posts)


@views.route("/like-post/<post_id>", methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(
        author=current_user.id, post_id=post_id).first()

    if not post:
        return jsonify({'error': 'Post does not exist.'}, 400)
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    return jsonify({"likes": len(post.likes), "liked": current_user.id in map(lambda x: x.author, post.likes)})