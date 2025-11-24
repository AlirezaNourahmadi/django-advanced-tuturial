from rest_framework import serializers
from blog.models import Post


# class PostSerializer(serializers.Serializer):
#     title = serializers.CharField(max_length=255)

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id","title","content","created_date","published_date","status"]