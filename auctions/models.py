from django.contrib.auth.models import AbstractUser
from django.db import models


class TimeStamp(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class User(AbstractUser):
    pass

class Listing(TimeStamp):
    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.FloatField()
    image_url = models.URLField(null=True, blank=True) 
    category = models.CharField(max_length=64, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    active = models.BooleanField(default=True)
    winner = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.title}: {self.starting_bid}"

class Bid(TimeStamp):
    amount = models.FloatField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids") 
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f"{self.amount}"


class Comment(TimeStamp):
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return f"{self.content}"

class Category():
    ...