from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    friends = models.ManyToManyField(User, blank=True, null=True, related_name="friends")
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    dob = models.DateField()
    imageUrl = models.CharField(max_length=2000, blank=True, default="")
    relationship = models.BooleanField()

    def __str__(self):
        return self.first_name + " " + self.last_name

class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="ownerGroup")
    users = models.ManyToManyField(Profile, blank=True, null=True, related_name="usersGroup")
    
    def __str__(self):
        return self.name

class Post(models.Model):
    userPost = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="post")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True, related_name="post")
    body = models.TextField()
    imageUrl = models.CharField(max_length=2000, blank=True, default="")
    likes = models.ManyToManyField(Profile, blank=True, null=True, related_name="likes")
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.body[:20]

class Comment(models.Model):
    userComment = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="comment")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comment")
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.body[:20]

