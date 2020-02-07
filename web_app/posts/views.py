from django.db.models import Count, Q
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import PostForm
from .models import Post, Author, PostView



def get_author(user):
    qs = Author.objects.filter(user=user)
    if qs.exists():
        return qs[0]
    return None


class SearchView(View):
    def get(self, request, *args, **kwargs):
        queryset = Post.objects.all()
        query = request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)|
                Q(ingredient__icontains=query)
            ).distinct()
        context = {
            'queryset': queryset
        }
        return render(request, 'search_results.html', context)


def search(request):
    queryset = Post.objects.all()
    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(ingredient__icontains=query)
        ).distinct()
    context = {
        'queryset': queryset
    }
    if len(queryset) == 0:
        messages.info(request, "Your search did not match any of our recipes.")
    return render(request, 'search_results.html', context)


# def get_category_count():
#     queryset = Post \
#         .objects \
#         .values('Cuisine__title') \
#         .annotate(Count('Cuisine__title'))
#     return queryset


class IndexView(View):
    def get(self, request, *args, **kwargs):
        random = Post.objects.order_by('?')[0:3]
        context = {
            'object_list': random,
        }
        if len(random) == 0:
            messages.info(request, "No posts to show yet.")
        return render(request, 'index.html', context)



def index(request):
    random = Post.objects.order_by('?')[0:3]
    context = {
        'object_list': random,
    }
    return render(request, 'index.html', context)



class PostDetailView(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'

    def get_object(self):
        obj = super().get_object()
        if self.request.user.is_authenticated:
            PostView.objects.get_or_create(
                user=self.request.user,
                post=obj
            )
        return obj

    def get_context_data(self, **kwargs):
        # category_count = get_category_count()
        # most_recent = Post.objects.order_by('-timestamp')[:3]
        context = super().get_context_data(**kwargs)
        # context['most_recent'] = most_recent
        context['page_request_var'] = "page"
        # context['category_count'] = category_count
        # context['form'] = self.form
        return context


def post_detail(request, id):
    category_count = get_category_count()
    most_recent = Post.objects.order_by('-timestamp')[:3]
    post = get_object_or_404(Post, id=id)

    if request.user.is_authenticated:
        PostView.objects.get_or_create(user=request.user, post=post)

    if request.method == "POST":
        if form.is_valid():
            form.instance.user = request.user
            form.instance.post = post
            form.save()
            return redirect(reverse("post-detail", kwargs={
                'id': post.pk
            }))
    context = {
        'post': post,
        'most_recent': most_recent,
        'category_count': category_count,
        'form': form
    }
    return render(request, 'post.html', context)


class PostCreateView(CreateView):
    model = Post
    template_name = 'post_create.html'
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create'
        return context

    def form_valid(self, form):
        form.instance.author = get_author(self.request.user)
        form.save()
        return redirect(reverse("post-detail", kwargs={
            'pk': form.instance.pk
        }))


def post_create(request):
    title = 'Create'
    form = PostForm(request.POST or None, request.FILES or None)
    author = get_author(request.user)
    if request.method == "POST":
        if form.is_valid():
            form.instance.author = author
            form.save()
            return redirect(reverse("post-detail", kwargs={
                'id': form.instance.id
            }))
    context = {
        'title': title,
        'form': form
    }
    return render(request, "post_create.html", context)


class PostUpdateView(UpdateView):
    model = Post
    template_name = 'post_create.html'
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update'
        return context

    def form_valid(self, form):
        form.instance.author = get_author(self.request.user)
        form.save()
        return redirect(reverse("post-detail", kwargs={
            'pk': form.instance.pk
        }))


def post_update(request, id):
    title = 'Update'
    post = get_object_or_404(Post, id=id)
    form = PostForm(
        request.POST or None,
        request.FILES or None,
        instance=post)
    author = get_author(request.user)
    if request.method == "POST":
        if form.is_valid():
            form.instance.author = author
            form.save()
            return redirect(reverse("post-detail", kwargs={
                'id': form.instance.id
            }))
    context = {
        'title': title,
        'form': form
    }
    return render(request, "post_create.html", context)


class PostDeleteView(DeleteView):
    model = Post
    success_url = '/my_posts'
    template_name = 'post_confirm_delete.html'


def post_delete(request, id):
    post = get_object_or_404(Post, id=id)
    post.delete()
    return redirect(reverse("post-list"))


def my_posts(request):
    present_author = Author.objects.filter(user=request.user)
    posts = Post.objects.order_by("-timestamp")
    final_posts = []
    for post in posts:
        if present_author[0] == post.author:
            final_posts.append(post)
    if len(final_posts) == 0:
        messages.info(request, "You have not posted any recipes.")
    return render(request, "my_posts.html",{'posts':final_posts})
    
def blog(request):  
    posts = Post.objects.order_by("-timestamp")
    if len(posts) == 0:
        messages.info(request, "Sorry, no posts to show.")
    return render(request, "blog.html",{'posts':posts})
