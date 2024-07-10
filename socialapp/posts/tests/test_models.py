from django.test import TestCase
from django.contrib.auth import get_user_model
from posts.models import Post, Comment

class PostModelTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(username="testuser", password="1234")
        self.post = Post.objects.create(
            title="Test Post",
            slug="test-post",
            content="This is a test post",
            author=self.user
        )
        
    def test_post_creation(self):
        self.assertEqual(self.post.title, "Test Post")
        self.assertEqual(self.post.slug, "test-post")
        self.assertEqual(self.post.content, "This is a test post")
        self.assertEqual(self.post.author, self.user)
        
        
class CommentModelTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(username="testuser", password="1234")
        self.user1 = get_user_model().objects.create_user(username="testuser1", password="1122")
        self.post = Post.objects.create(
            title="Test Post",
            slug="test-post",
            content="This is a test post",
            author=self.user
        )
        self.comment = Comment.objects.create(
            user=self.user1,
            post=self.post,
            content="Content of a comment"
        )
        
    def test_comment_creation(self):
        self.assertEqual(self.comment.user, self.user1)
        self.assertEqual(self.comment.post, self.post)
        self.assertEqual(self.comment.content, "Content of a comment")
        