from django.core import paginator
from django.shortcuts import get_object_or_404, render
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from .forms import EmailPostForm
from django.core.mail import send_mail

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



def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status="published")
    sent = False
    if request.method == "POST":
        # 填好的表
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n {cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, "admin@myblog.com", [cd["to"]])
            sent = True
    else:
        # 空的表
        form = EmailPostForm()
    return render(request, "blog/post/share.html", {"post":post, "form":form, "sent":sent})