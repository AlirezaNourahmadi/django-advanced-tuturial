from django.urls import include, path
from . import views
from django.views.generic import TemplateView, RedirectView


app_name = "blog"

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    # path("fbv-index/",views.indexView,name="fbv-test"),
    # path("cbv-index/", TemplateView.as_view(template_name="index.html", extra_context={"name":"alireza"})),
    # path("cbv-index/",views.IndexView.as_view(),name="cbv-index"),
    # path("go-to-maktabkhooneh/",views.RedirectToMaktabView.as_view(),name="redirect-to-maktabkhooneh"),
    path("post/", views.PostListView.as_view(), name="post-list"),
    path("post/<int:pk>/", views.PostDetailView.as_view(), name="post-detail"),
    path("post/create/", views.PostCreateView.as_view(), name="post-create"),
    path("post/<int:pk>/update/", views.PostUpdateView.as_view(), name="post-update"),
    path("post/<int:pk>/delete/", views.PostDeleteView.as_view(), name="post-delete"),
    path("post/", views.api_post_list_view, name="post-list"),
    # api path
    path("api/v1/", include("blog.api.v1.urls")),
]
