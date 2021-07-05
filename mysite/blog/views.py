from django.core import paginator
from django.shortcuts import get_object_or_404, render
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.


def post_list(request):
    object_list = Post.published.all()
    paginator = Paginator(object_list, 3)  # 每页三个
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)  # 如果页数不是一个整数，则显示第一页
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)  # 如果页数超出范围，则显示最后一页

    return render(request, "blog/post/list.html", {"page": page, "posts": posts})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status="published",
                             publish__year=year, publish__month=month, publish__day=day)
    return render(request, "blog/post/detail.html", {"post": post})
