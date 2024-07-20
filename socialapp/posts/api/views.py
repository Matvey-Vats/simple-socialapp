from rest_framework import viewsets, generics, serializers
from rest_framework.pagination import PageNumberPagination
from posts.models import Post, Comment, TagPost
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminOrReadOnly


from .serializers import PostSerializer, CommentSerializer, TagPostSerializer


class PostAPIListPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = "page_size"
    max_page_size = 10000

# class PostAPIList(generics.ListCreateAPIView):
#     queryset = Post.published.all().order_by('-time_create')
#     serializer_class = PostSerializer
#     pagination_class = PostAPIListPagination
#     permission_classes = (IsAuthenticated,)
    
    
#     def perform_create(self, serializer):
#         serializer.save(author=self.request.user)
    
    
      
# class PostDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Post.published.all().order_by('-time_create')
#     serializer_class = PostSerializer
#     permission_classes = (IsAdminOrReadOnly,)
    
# class PostUpdateAPIView(generics.RetrieveUpdateAPIView):
#     queryset = Post.published.all().order_by('-time_create')
#     serializer_class = PostSerializer
#     permission_classes = (IsAuthenticated,)
    
#     def perform_update(self, serializer):
#         instance = self.get_object()
#         if 'photo' not in self.request.data and instance.photo:
#             serializer.save(image=instance.photo)
#         else:
#             serializer.save()
            

class PostAPIList(viewsets.ModelViewSet):
    queryset = Post.published.all().order_by("-time_create")
    serializer_class = PostSerializer
    pagination_class = PostAPIListPagination
    permission_classes = [IsAuthenticated,]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        
    def perform_update(self, serializer):
        instance = self.get_object()
        if 'photo' not in self.request.data and instance.photo:
            serializer.save(image=instance.photo)
        else:
            serializer.save()
            
    
    
    
class CommentAPIList(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    def perform_update(self, serializer):
        instance = self.get_object()
        if 'parent' in self.request.data:
            parent_comment = Comment.objects.get(pk=self.request.data['parent'])
            if parent_comment.post != instance.post:
                raise serializers.ValidationError("Комментарий должен пренадлежать тому же посту")
        serializer.save()
             
class TagPostApiList(viewsets.ModelViewSet):
    queryset = TagPost.objects.all()
    serializer_class = TagPostSerializer
    