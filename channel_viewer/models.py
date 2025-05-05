from django.db import models
from django.contrib.auth.models import User

class YouTubeChannel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    channel_name = models.CharField(max_length=100)
    channel_id = models.CharField(max_length=100, blank=True)
    is_whitelisted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'channel_id')
    
    def __str__(self):
        return f"{self.channel_name} (User: {self.user.username})"

class YouTubeVideo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video_id = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    channel = models.ForeignKey(YouTubeChannel, on_delete=models.CASCADE)
    published_at = models.DateTimeField()
    thumbnail_url = models.URLField()
    is_whitelisted = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('user', 'video_id')
    
    def __str__(self):
        return self.title

class FavoritePlaylist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    videos = models.ManyToManyField(YouTubeVideo)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s {self.name}"