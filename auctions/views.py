from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Bid, Comment
from .forms import ListingForm, CommentForm

def index(request):
    if "watchlist" not in request.session:
        request.session["watchlist"] = []
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(active=True)
    })

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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required(login_url='login')
def create(request):
    if request.method == 'POST':
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = Listing(**form.cleaned_data, user=request.user)
            listing.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/create.html", {
            "form": form
        })
    else:
        return render(request, "auctions/create.html", {
            "form": ListingForm()
        })

def listing(request, listing_id):
    if "watchlist" not in request.session:
        request.session["watchlist"] = []
    try:
        listing = Listing.objects.get(pk=listing_id)
    except Listing.DoesNotExist:
        raise Http404("Listing not found")
    closable = (request.user.id == listing.user.id) and listing.active
    add_able = listing.id not in request.session["watchlist"]
    remove_able = listing.id in request.session["watchlist"]
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "closable": closable,
        "active": listing.active,
        "winner": (request.user.id == listing.winner),
        "form": CommentForm(),
        "comments": listing.comments.all(),
        "add_able": add_able,
        "remove_able": remove_able,
    })

def bid(request, listing_id):
    try:
        listing = Listing.objects.get(id=listing_id)
    except Listing.DoesNotExist:
        raise Http404("Listing not found")
    
    amount = float(request.POST["amount"])
    bids = [bid.amount for bid in listing.bids.all()]
    if not amount or amount < listing.starting_bid:
        return HttpResponseBadRequest("Bad Request: amount invalid")
    if bids and amount < max(bids):
        return HttpResponseBadRequest("Bad Request: amount invalid")
    
    bid = Bid(amount=amount, listing=listing, user=request.user)
    bid.save()
    Listing.objects.filter(pk=listing_id).update(starting_bid=amount)

    return HttpResponseRedirect(reverse("listing", args=(listing_id, )))

@login_required(login_url='login')
def add_watchlist(request, listing_id):
    request.session["watchlist"] += [listing_id]
    return HttpResponseRedirect(reverse("listing", args=(listing_id, )))

@login_required(login_url='login')
def remove_watchlist(request, listing_id):
    request.session["watchlist"].remove(listing_id)
    request.session.modified = True
    return HttpResponseRedirect(reverse("listing", args=(listing_id, )))

def close(request):
    id = request.POST["id"]
    listing = Listing.objects.get(pk=id)
    winner = listing.bids.all().order_by('-amount').first().user.id 
    Listing.objects.filter(pk=id).update(active=False, winner=winner)
    return HttpResponseRedirect(reverse("listing", args=(id, )))

def comment(request, listing_id):
    try:
        listing = Listing.objects.get(id=listing_id)
    except Listing.DoesNotExist:
        raise Http404("Listing not found")

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = Comment(**form.cleaned_data, user=request.user, listing=listing)
        comment.save()
        return HttpResponseRedirect(reverse("listing", args=(listing_id, )))
    else:
        return HttpResponseBadRequest("Bad Request")

@login_required(login_url='login')
def watchlist(request):
    if "watchlist" not in request.session:
        request.session["watchlist"] = []
    watch_list = request.session["watchlist"]
    listings = Listing.objects.filter(id__in=watch_list).values()
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })

@login_required(login_url='login')
def categories(request):
    listings = Listing.objects.all()
    lst = set()
    for listing in listings:
        lst.add(listing.category)
    return render(request, "auctions/categories.html", {
        "categories": lst
    })

@login_required(login_url='login')
def category(request, category):
    listings = Listing.objects.filter(category=category, active=True)
    return render(request, "auctions/category.html", {
        "listings": listings,
        "category": category
    })