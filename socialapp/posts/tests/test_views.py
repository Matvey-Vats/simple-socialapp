from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from posts.models import Post

class PostListViewTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(username='testuser', password='1234')
        self.post1 = Post.objects.create(
            title="Test Post 1",
            slug="test-post-1",
            content="This is a post 1",
            author=self.user,
            is_published=Post.Status.PUBLISHED,
        )
        
        self.post2 = Post.objects.create(
            title="Test Post 2",
            slug="test-post-2",
            content="This is a post 2",
            author=self.user,
            is_published=Post.Status.PUBLISHED,
        )
        
        
    def test_view_url_exists_at_proper_location(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
    def test_view_uses_correct_template(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts/index.html')
        
class PostDetailViewTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(username="testuser", password="1234")
        self.post = Post.objects.create(
            title="Test Post",
            slug="test-post",
            content="This is a post",
            author=self.user,
            is_published=Post.Status.PUBLISHED,
        )
        
    def test_view_url_exists_at_proper_location(self):
        response = self.client.get(f'/post/{self.post.slug}/')
        self.assertEqual(response.status_code, 200)
        
        
    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('post_detail', kwargs={"post_slug": self.post.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'post/post_detail.html')
        
    def test_context_data(self):
        self.client.login(username="testuser", password="1234")
        response = self.client.get(reverse("post_detail", kwargs={"post_detail": self.post.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('likes' in response.context)
        self.assertFalse(response.content['liked'])
        