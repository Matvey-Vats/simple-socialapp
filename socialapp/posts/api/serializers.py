from posts.models import Post, Comment, TagPost
from rest_framework import serializers
from django.urls import reverse


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())
    parent = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), required=False, allow_null=True)
    class Meta:
        model = Comment
        fields = '__all__'
        
    def validate_parent(self, value):
        if value and value.post != self.initial_data['post']:
            raise serializers.ValidationError("Комментарий должен принадлежать к тому же посту.")
        return value
    
    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        return super().create(validated_data)
        
        
class TagPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagPost
        fields = ['id', 'tag']

class PostSerializer(serializers.ModelSerializer):
    # comments_count = serializers.SerializerMethodField()
    author = serializers.ReadOnlyField(source="author.username")
    comments = CommentSerializer(many=True, read_only=True)
    photo = serializers.ImageField(required=False)
    # tags = TagPostSerializer(many=True)
    tags = serializers.SlugRelatedField(slug_field='tag', queryset=TagPost.objects.all(), many=True)
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'photo', 'author', 'total_likes', 'total_comments', 'tags', 'time_create', 'time_update', 'is_published', 'comments']
        
    def get_comments_count(self, obj):
        return obj.comments.count()
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def validate_tags(self, value):
        if len(value) > 8:
            raise serializers.ValidationError("Нельзя добавлять больше 8 тегов")
        
    
    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        post = Post.objects.create(**validated_data)
        for tag_data in tags_data:
            tag, created = TagPost.objects.get_or_create(name=tag_data.name)
            post.tags.add(tag)
        return post
    
    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', [])
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.photo = validated_data.get('photo', instance.photo)
        instance.is_published = validated_data.get('is_published', instance.is_published)
        instance.save()

        instance.tags.clear()
        for tag_data in tags_data:
            tag, created = TagPost.objects.get_or_create(tag=tag_data.tag)
            instance.tags.add(tag)
            
        return instance