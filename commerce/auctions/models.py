from typing import Union
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator


class User(AbstractUser):

    def __str__(self) -> str:
        return self.first_name


class Category(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self) -> str:
        return self.name


class Listing(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=100, null=False, blank=False)
    description = models.CharField(max_length=200)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="category",
        null=True,
        blank=True,
    )
    photo = models.URLField(
        null=True,
        blank=True,
    )
    starting_bid = models.FloatField(
        validators=[MinValueValidator(1.0)],
    )
    is_active = models.BooleanField(default=True)

    def get_winner(self) -> Union["Bid", None]:
        bids = self.listing_bids.all()
        if bids:
            bids: list[Bid] = sorted(bids, key=lambda x: x.value, reverse=True)
            return bids[0]
        return None

    def get_current_price(self) -> float:
        winner = self.get_winner()
        if winner:
            return winner.value
        return self.starting_bid

    def __str__(self) -> str:
        return f"{self.title} : {self.seller}"


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    value = models.FloatField(
        validators=[MinValueValidator(1.0)],
    )
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="listing_bids"
    )

    def __str__(self) -> str:
        return f"{self.user} : {self.value} : {self.listing}"


class Commentary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    text = models.CharField(blank=False, null=False, max_length=300)
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="listing_comments"
    )

    def __str__(self) -> str:
        return f"{self.user} : {self.text} : {self.listing}"


class WatchlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="watchlist_included"
    )
