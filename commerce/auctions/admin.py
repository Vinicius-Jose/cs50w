from django.contrib import admin
from .models import Listing, Commentary, Bid, Category, User, WatchlistItem

# Register your models here.

admin.site.register(Listing)
admin.site.register(Commentary)
admin.site.register(Bid)
admin.site.register(Category)
admin.site.register(User)
admin.site.register(WatchlistItem)
