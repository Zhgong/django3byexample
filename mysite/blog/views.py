from django.core import paginator
from django.shortcuts import get_object_or_404, render
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import TrigramSimilarity

# Create your views here.


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = "posts"
    paginate_by = 3
    template_name = "blog/post/list.html"

    def get_context_data(self, **kwargs):
        # 在listview中url参数是通过self.kwargs来传递的，get_context_data里面只能接收通过?号传递的查询参数
        tag_slug = self.kwargs.get("tag_slug")
        object_list = Post.published.all()

        tag = None
        if tag_slug:
            tag = get_object_or_404(Tag, slug=tag_slug)
            object_list = object_list.filter(tags__in=[tag])
        context = super().get_context_data(**kwargs)
        context['posts'] = object_list
        context['tag'] = tag
        return context


class PostDetailView(TemplateView):
    model = Post
    template_name = "blog/post/detail.html"

    def get_context_data(self, *args, **kwargs):
        print(args)
        print(kwargs)
        context = super(PostDetailView, self).get_context_data(*args, **kwargs)

        post = get_object_or_404(Post, slug=kwargs["post"], status="published",
                                 publish__year=kwargs["year"], publish__month=kwargs["month"], publish__day=kwargs["day"])

        # 列出相似的推文
        # 获取此推文所有的标签，并将结果扁平化处理 [(1,), (2,), (3,) ...] ==> [1, 2, 3, ...]
        post_tags_ids = post.tags.values_list("id", flat=True)
        similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(
            id=post.id)  # 查找类似的推文，__in 是内置的查找方法
        # 返回的结果是一个查询对象，如果把它列表化，其中会有重复的元素，如果某个推文其中有两个tag符合要求，这个推文会在列表中出现两次。

        # 将上一步得到的结果进行归类汇总（计数），然后排序。
        similar_posts = similar_posts.annotate(same_tags=Count(
            'tags')).order_by('-same_tags', '-publish')[:4]

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
            new_comment = comment_form.save(commit=False)  # 创建对象但是不保存
            new_comment.post = post  # 链接post
            new_comment.save()  # 保存

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
    return render(request, "blog/post/share.html", {"post": post, "form": form, "sent": sent})


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector(
                'title', weight='A') + SearchVector('body', weight='B')  # A:1.0, B:0.4 给予标题更大的权重
            search_query = SearchQuery(query)
            results = Post.published.annotate(
                similarity=TrigramSimilarity('title', query),
            ).filter(similarity__gte=0.1).order_by('-similarity')  # 传回搜索结果 筛选评相似度大于0.1的结果
    return render(request,
                  'blog/post/search.html',
                  {'form': form,
                   'query': query,
                   'results': results
                   })
