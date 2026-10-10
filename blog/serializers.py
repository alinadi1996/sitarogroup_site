from rest_framework import serializers

class BlogSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)
    content = serializers.CharField(max_length=500)
    author = serializers.CharField(max_length=100)
    cover = serializers.ImageField()