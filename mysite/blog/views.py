from django.core import paginator
from django.shortcuts import get_object_or_404, render
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.views.generic.base import TemplateView

# Create your views here.

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = "posts"
    paginate_by = 3
    template_name = "blog/post/list.html"



class PostDetailView(TemplateView):
    model = Post
    template_name = "blog/post/detail.html"

    def get_context_data(self, *args, **kwargs):
        print("mark")
        print(args)
        print(kwargs)
        context = super(PostDetailView, self).get_context_data(*args, **kwargs)

        post = get_object_or_404(Post, slug=kwargs["post"], status="published",
                             publish__year=kwargs["year"], publish__month=kwargs["month"], publish__day=kwargs["day"])
        context['post'] = post
        return context

