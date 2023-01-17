from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .common import paginator
from .forms import PostForm
from .models import Group, Post

AMOUNT = 10
User = get_user_model()


def index(request):

    template = 'posts/index.html'
    post_list = Post.objects.select_related()
    text = 'Это главная страница проекта Yatube'
    title = 'Main page'

    context = {
        'text': text,
        'posts': post_list,
        'title': title,
        'page_obj': paginator(request, post_list, AMOUNT),
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()

    context = {
        'title': 'Сообщества',
        'group': group,
        'page_obj': paginator(request, post_list, AMOUNT),
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    user = get_object_or_404(User, username=username)
    post_list = user.posts.all()
    posts_count = post_list.count()
    title = f'Профайл пользователя {username}'

    context = {
        'posts_count': posts_count,
        'title': title,
        'page_obj': paginator(request, post_list, AMOUNT),
        'author': user,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post_text': post.text,
        'post': post,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'

    if request.method == 'POST':
        form = PostForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', post.author.username)

        return render(request, template, {
            'form': form,
            'title': 'Новый пост',
        })

    form = PostForm()
    return render(request, template, {
        'form': form,
        'title': 'Новый пост',
    })


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'

    post = get_object_or_404(Post, pk=post_id)
    current_user = request.user

    if current_user != post.author:
        return redirect('posts:post_detail', post_id)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)

        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect('posts:post_detail', post_id)

        return render(request, template, {
            'form': form,
            'title': 'Редактировать пост',
            'is_edit': True,
            'post': post,
        })
    form = PostForm()
    return render(request, template, {
        'form': form,
        'title': 'Редактировать пост',
        'is_edit': True,
        'post_id': post_id,
    })
