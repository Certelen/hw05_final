from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect, reverse

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm


def paginator(request, post_list):
    paginator = Paginator(post_list, settings.MAX_COUNT_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):

    post_list = Post.objects.all()
    page_obj = paginator(request, post_list)

    context = {
        'page_obj': page_obj,
        'index': True
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):

    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = paginator(request, post_list)

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    follow = (
        request.user.is_authenticated
        and user != author
        and Follow.objects.filter(user=user, author=author).exists()
    )
    post_list = author.posts.all()
    page_obj = paginator(request, post_list)

    context = {
        'author': author,
        'page_obj': page_obj,
        'following': follow,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    comment_form = CommentForm()

    context = {
        'post': post,
        'comments': comments,
        'form': comment_form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author)

    context = {
        'form': form
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_url = reverse('posts:post_detail', kwargs={'post_id': post.id})
    if request.user != post.author:
        return redirect(post_url)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if form.is_valid():
        form.save()
        return redirect(post_url)

    context = {'form': form,
               'IS_EDIT': True}
    return render(request, 'posts/create_post.html', context)


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
    posts = Post.objects.filter(author__following__user=request.user)

    page_obj = paginator(request, posts)
    context = {
        'page_obj': page_obj,
        'follow': True,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    follow_user = request.user
    follow_author = User.objects.get(username=username)
    if follow_user != follow_author:
        Follow.objects.get_or_create(
            user=follow_user,
            author=follow_author
        )

    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    unfollow_user = request.user
    unfollow_author = get_object_or_404(User, username=username)
    unfollow = Follow.objects.filter(
        user=unfollow_user,
        author=unfollow_author
    )
    unfollow.delete()
    return redirect('posts:profile', username=username)
