from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

from taggit.managers import TaggableManager


class PublishedManager(models.Manager):
    """Custom Manager to filter out only published posts."""

    def get_queryset(self):
        """Override the default get_queryset method to include filter."""
        return super().get_queryset().filter(status=self.model.Status.PUBLISHED)


class Post(models.Model):
    """Represents a single blog post."""

    objects = models.Manager()  # Default Manager
    published = PublishedManager()  # Custom Manager to easily get all published posts

    class Status(models.TextChoices):
        """Defines the possible status choices for a blog post (Draft/Published)."""
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=250)
    slug = models.SlugField(
        max_length=250,
        unique_for_date='publish'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blog_posts'
    )
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.DRAFT
    )

    tags = TaggableManager()

    # Metadata for Ordering and Indexing (for efficient database queries)
    class Meta:
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish']),
        ]

    def __str__(self):
        """Returns the title as the string representation of the Post object."""
        return str(self.title)

    def get_absolute_url(self):
        return reverse(
            'blog:post_detail',
            args=[
                self.publish.year,  # pylint: disable=no-member
                self.publish.month,  # pylint: disable=no-member
                self.publish.day,  # pylint: disable=no-member
                self.slug  # pylint: disable=no-member
            ]
        )


class Comment(models.Model):
    """Represents a single comment on a blog post."""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['created']),
        ]

    def __str__(self):
        return f"Comment by {self.name} on {self.post}"
