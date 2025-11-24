from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import PostSerializer
from blog.models import Post


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticatedOrReadOnly])
def postList(request):
    if request.methods == "GET":
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    elif request.methods == "POST":
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticatedOrReadOnly])
def postDetail(request, id):
    post = get_object_or_404(Post, pk=id)
    if request.methods == "GET":
        serializer = PostSerializer(post)
        return Response(serializer.data)
    elif request.methods == "PUT":
        serializer = PostSerializer(post, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.methods == "DELETE":
        post.delete()
        return Response({"detail": "item removed successfully"},status=status.HTTP_204_NO_CONTENT)

    # try:
        # post = Post.objects.get(pk=id)
        # serializer = PostSerializer(post)
        # return Response(serializer.data)
    # except Post.DoesNotExist:
        # return Response({"detail":"post does not exist"}, status=status.HTTP_404_NOT_FOUND)
