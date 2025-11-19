from django.shortcuts import redirect, render
from django.views.generic import ListView, TemplateView
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import ContactForm, PostForm
from .models import Post
# Create your views here.

# function based view to show index page
"""
def indexView(request):

    name = "alireza"
    context = {"name":name}
    return render(request,"index.html",context)
"""


class IndexView(TemplateView):
    """
    class based view to show index page
    """
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["name"] = "alireza"
        context["posts"] = Post.objects.all()

        return context


"""
    FBV for derirect to maktabkhooneh
    
    def redirectToMaktab(request):
    return redirect("https://www.maktabkhooneh.com/")
"""


class RedirectToMaktabView(RedirectView):
    permanent = True
    url = "https://www.maktabkhooneh.com/"


class PostListView(LoginRequiredMixin,ListView):
    model = Post
    # queryset = Post.objects.all()
    ordering = "id"
    context_object_name = "posts"
    paginate_by = 2

    # def get_queryset(self):
    #     posts=Post.objects.filter(status=True)
    #     return posts


class PostDetailView(LoginRequiredMixin,DetailView):
    model = Post


# class PostCreateView(FormView):
#     template_name = "post_create.html"
#     form_class = PostCreateForm
#     pass


"""
class PostCreateView(FormView):
    template_name = "contact.html"
    form_class = PostForm
    success_url = '/blog/post/'
    
    
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
"""


class PostCreateView(LoginRequiredMixin,CreateView):
    model = Post
    # fields = "__all__"
    form_class = PostForm
    success_url = "/blog/post/"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin,UpdateView):
    model = Post
    form_class = PostForm
    success_url = "/blog/post/"
    
class PostDeleteView(LoginRequiredMixin,DeleteView):
    model = Post
    success_url = "/blog/post/"
