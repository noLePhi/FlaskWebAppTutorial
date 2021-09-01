from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import Post, User, Comment, Like
from . import db
from bs4 import BeautifulSoup
import requests
import os
import json
import lxml

articles = Blueprint("articles", __name__)

@articles.route("/")
@articles.route("/articles/last", methods=['GET', 'POST'])
@login_required
def last_articles():
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

@articles.route("/")
@articles.route("/articles/recommended", methods=['GET', 'POST'])
@login_required
def recommended_articles():
    return render_template('articles_reco.html', user=current_user)