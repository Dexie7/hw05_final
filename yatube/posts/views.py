from django.conf import settings
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from . models import Follow, Group, Post, User
from .forms import CommentForm, PostForm


def page_paginator(request, post_list):
    return Paginator(post_list, settings.MAX_PAGE_COUNT).get_page(
        request.GET.get('page')
    )


def index(request):
    return render(request, 'posts/index.html', {
        'page_obj': page_paginator(request, Post.objects.all()),
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    return render(request, 'posts/group_list.html', {
        'group': group,
        "page_obj": page_paginator(request, group.posts.all()),
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    try:
        following = Follow.objects.get(user=request.user, author=author)
    except Exception:
        following = False
    return render(request, 'posts/profile.html', {
        'page_obj': page_paginator(request, author.posts.all()),
        'author': author,
        'following': following,
    })


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    return render(request, 'posts/post_detail.html', {
        'count_of_posts': post.author.posts.all().count(),
        'post': post,
        'form': form,
        'comments': post.comments.all(),
    })


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect(
        'posts:profile',
        username=request.user.username
    )


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post.pk)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.pk)
    return render(request, 'posts/create_post.html', {
        'form': form,
        'post': post,
        'is_edit': True,
    })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    follow_post = Post.objects.filter(author__following__user=request.user)
    return render(request, 'posts/follow.html', {
        'page_obj': page_paginator(request, follow_post),
    })


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    unfollow = get_object_or_404(Follow, user=request.user, author__username=username)
    if unfollow is not None:
        unfollow.delete()
    return redirect('posts:profile', username=username)
