from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
# Create your models here.



#getting user model object
# user = get_user_model()

class Post(models.Model):
    '''
    This is a class to define posts for blog
    '''
    author = models.ForeignKey("accounts.Profile",on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True)
    title = models.CharField(max_length=250)
    content = models.TextField()
    status = models.BooleanField()
    category = models.ForeignKey("Category", on_delete=models.SET_NULL, null=True)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    published_date = models.DateTimeField()

    def __str__(self):
        return self.title
    
    def get_snippet(self):
        return self.content[0:10]
    
    def get_absolute_api_url(self):
        return reverse("blog:api-v1:post-detail", kwargs={"pk": self.pk})
    

class Category(models.Model):
    '''
    This is a class to define categories for blog
    '''
    name = models.CharField(max_length=100)


    def __str__(self):
        return self.name