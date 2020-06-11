from django.db.models import Count
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from blog.models import Comment, Post, Tag


def serialize_post(post):
    return {
        "title": post.title,
        "teaser_text": post.text[:200],
        "author": post.author.username,
        "comments_amount": post.comments_count,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_count,
    }


def index(request):
    posts = Post.objects.prefetch_tags().prefetch_related('author')
    popular_posts = posts.get_popular_posts()[:5]
    most_popular_posts = popular_posts.fetch_comments_count()

    fresh_posts = posts.order_by('-published_at')[:5]
    most_fresh_posts = fresh_posts.fetch_comments_count()

    most_popular_tags = Tag.objects.prefetch_related('posts').popular()[:5]

    context = {
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    posts = Post.objects.prefetch_tags().prefetch_related('comments__author', 'author')
    post = get_object_or_404(posts, slug=slug)

    comments = post.comments.all()

    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    likes = post.likes.all()

    related_tags = post.tags.all()

    serialized_post = {
        "title": post.title,
        "text": post.text,
        "author": post.author.username,
        "comments": serialized_comments,
        'likes_amount': likes.count(),
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [serialize_tag(tag) for tag in related_tags],
    }

    most_popular_tags = Tag.objects.popular()[:5]

    popular_posts = posts.get_popular_posts()[:5]
    most_popular_posts = popular_posts.fetch_comments_count()

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    most_popular_tags = Tag.objects.popular()[:5]
    tag = get_object_or_404(Tag, title=tag_title)

    posts = Post.objects.prefetch_tags().prefetch_related('author')
    popular_posts = posts.get_popular_posts()[:5]
    most_popular_posts = popular_posts.fetch_comments_count()

    related_posts = posts.filter(tags=tag)[:20]
    related_comments_count_posts = related_posts.fetch_comments_count()

    context = {
        "tag": tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        "posts": [serialize_post(post) for post in related_comments_count_posts],
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
