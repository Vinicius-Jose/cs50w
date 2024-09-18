from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .forms import BidForm, CommentaryForm, ListingForm

from .models import Category, Listing, User, WatchlistItem


def index(request):
    return render(
        request,
        "auctions/index.html",
        {"listings": Listing.objects.filter(is_active=True).all()},
    )


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def listing(request: HttpRequest, listing_id: int = 0):
    if request.method == "POST":
        if listing_id:
            listing = Listing.objects.get(id=listing_id)
            listing.is_active = not listing.is_active
            listing.save()
        else:
            listing = ListingForm(seller=request.user, data=request.POST)
            if not listing.errors:
                listing = listing.save()
        return redirect("listing", listing_id=listing.id)
    elif listing_id:
        return __render_listing_page(request, listing_id)

    return render(
        request,
        "auctions/create_listing.html",
        {"form": ListingForm(seller=request.user)},
    )


def __render_listing_page(request, listing_id: int):
    listing = Listing.objects.get(id=listing_id)
    bids = listing.listing_bids.all()
    winner = listing.get_winner()
    is_winning = winner.user.id == request.user.id if winner else False
    have_make_bid = request.user.id in (bid.user.id for bid in bids)
    watchlisted = False
    if request.user.is_authenticated:
        item = WatchlistItem.objects.filter(user=request.user, listing=listing)
        watchlisted = item.exists()
    return render(
        request,
        "auctions/listing.html",
        {
            "listing": listing,
            "bids": bids,
            "number_bids": len(bids),
            "winner": winner,
            "is_winning": is_winning,
            "have_make_bid": have_make_bid,
            "watchlisted": watchlisted,
            "bid_form": BidForm(user=request.user, listing=listing),
            "commentary_form": CommentaryForm(user=request.user, listing=listing),
        },
    )


@login_required
def bid(request: HttpRequest, listing_id: int):
    if request.method == "POST":
        listing = Listing.objects.get(id=listing_id)
        bid = BidForm(user=request.user, listing=listing, data=request.POST)
        if not bid.errors:
            bid.save()
    return redirect("listing", listing_id=listing_id)


@login_required
def watchlist(request: HttpRequest, listing_id: int = 0):
    if request.method == "POST" and listing_id:
        listing = Listing.objects.get(id=listing_id)
        watchlist = request.user.watchlist.all()
        item = WatchlistItem.objects.filter(user=request.user, listing=listing)
        if item.exists():
            item.first().delete()
        else:
            watchlist_item = WatchlistItem(user=request.user, listing=listing)
            watchlist_item.save()
        return redirect("listing", listing_id=listing_id)
    return render(
        request,
        "auctions/watchlist.html",
        {"watchlist": request.user.watchlist.all()},
    )


@login_required
def commentary(request: HttpRequest, listing_id: int):
    if request.method == "POST":
        listing = Listing.objects.get(id=listing_id)
        comment = CommentaryForm(user=request.user, listing=listing, data=request.POST)
        if not comment.errors:
            comment.save()
    return redirect("listing", listing_id=listing_id)


@login_required
def category(request: HttpRequest, category_id: int = 0):
    if category_id:
        listings = Listing.objects.filter(category_id=category_id)
        return render(request, "auctions/index.html", {"listings": listings.all()})
    return render(
        request, "auctions/category.html", {"categories": Category.objects.all()}
    )
