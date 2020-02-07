from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from posts.views import (
    index,
    search,
    post_detail,
    post_create,
    post_update,
    post_delete,
    IndexView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    my_posts,
    blog,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='home'),
    path('blog/', blog, name='post-list'),
    path('search/', search, name='search'),
    path('create/', PostCreateView.as_view(), name='post-create'),
    path('post/<pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/<pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('accounts/',include('account.urls')),
    path('my_posts',my_posts,name='my_posts'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
