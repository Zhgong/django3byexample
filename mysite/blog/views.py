from django.core import paginator
from django.shortcuts import get_object_or_404, render
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count

# Create your views here.

# class PostListView(ListView):
#     queryset = Post.published.all()
#     context_object_name = "posts"
#     paginate_by = 3
#     template_name = "blog/post/list.html"

def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3) # 3 posts in each page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'page': page, 'posts': posts, 'tag': tag})

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
        
        #列出相似的推文
        post_tags_ids = post.tags.values_list("id", flat=True) # 获取此推文所有的标签，并将结果扁平化处理 [(1,), (2,), (3,) ...] ==> [1, 2, 3, ...]
        similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id) # 查找类似的推文，__in 是内置的查找方法
        # 返回的结果是一个查询对象，如果把它列表化，其中会有重复的元素，如果某个推文其中有两个tag符合要求，这个推文会在列表中出现两次。

        # 将上一步得到的结果进行归类汇总（计数），然后排序。    
        similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]


        comments = post.comments.filter(active=True)
        comment_form = CommentForm()
        context['post'] = post
        context['comments'] = comments
        context['comment_form'] = comment_form
        context['similar_posts'] = similar_posts

    
        return context

    def post(self, request, *args, **kwargs):
        context = self.post_context_data(request, *args, **kwargs)
        return self.render_to_response(context)

    def post_context_data(self, request, *args, **kwargs):
        context = super(PostDetailView, self).get_context_data(*args, **kwargs)

        post = get_object_or_404(Post, slug=kwargs["post"], status="published",
                             publish__year=kwargs["year"], publish__month=kwargs["month"], publish__day=kwargs["day"])

        
        comments = post.comments.filter(active=True)
        comment_form = CommentForm(data=request.POST)

        # 保存到数据库
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False) # 创建对象但是不保存
            new_comment.post = post # 链接post
            new_comment.save() # 保存

        context['post'] = post
        context['comments'] = comments
        context['comment_form'] = comment_form
        context['new_comment'] = True
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