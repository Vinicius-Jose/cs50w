from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Post, User
import json


def index(request):
    page = get_page(request)
    obj_list = Post.objects.all().order_by("-timestamp").all()
    page = paginator(obj_list, page)

    return render(request, "network/index.html", page)


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
                "network/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "network/login.html")


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
                request, "network/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request, "network/register.html", {"message": "Username already taken."}
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def post(request: HttpRequest, post_id: int = 0):
    if request.method == "GET":
        response = None
        page = get_page(request)
        if post_id:
            response = Post.objects.get(id=post_id)
            response = response.serializer()
            response["user"] = response["user"].id
            response["likes"] = [user.id for user in response["likes"]]
            return JsonResponse(response, status=200)
        elif page:
            obj_list = Post.objects.all().order_by("-timestamp").all()
            page = paginator(obj_list, page)
            return JsonResponse(page, status=200)
    elif request.method == "POST":
        user = request.user
        text = request.POST.get("postContent")
        post = Post(user=user, text=text)
        post.save()
        return redirect("index")
    elif request.method == "PUT":
        body = json.loads(request.body)
        post = Post.objects.get(id=post_id)
        if post.user == request.user:
            post.text = body.get("text", post.text)
            post.save()
            response = post.serializer()
            response["user"] = response["user"].id
            response["likes"] = [user.id for user in response["likes"]]
            return JsonResponse(response, status=200)
    return JsonResponse({"message": "Method not allowed"}, status=405)


def paginator(obj_list: list, page: int = 0):
    paginator = Paginator(obj_list, 10)
    if page > paginator.num_pages:
        page = paginator.num_pages
    response = paginator.get_page(page)
    response = {
        "results": [item.serializer() for item in response.object_list],
        "number_of_pages": paginator.num_pages,
        "current_page": page,
        "range": range(1, paginator.num_pages + 1),
    }
    return response


def like(request: HttpRequest):
    user = request.user
    post_id = json.loads(request.body).get("post_id")
    post = Post.objects.get(id=post_id)
    if request.method == "POST":
        user.liked_posts.add(post)
        user.save()
    elif request.method == "DELETE":
        user.liked_posts.remove(post)
        user.save()
    return JsonResponse({"message": "Operation finished"}, status=201)


def profile(request: HttpRequest, user_id: int):
    page = get_page(request)
    user = User.objects.get(id=user_id)
    content = user.posts.order_by("-timestamp").all()
    content = paginator(content, page)
    content["user"] = user
    return render(request, "network/profile.html", content)


def get_page(request):
    try:
        page = int(request.GET.get("page", 1))
    except:
        page = 0
    return page


@login_required
def follow(request: HttpRequest, user_id: int = 0):
    user = request.user

    if request.method == "POST":
        user_follow = User.objects.get(id=user_id)
        if user_follow in user.following_list.all():
            user.following_list.remove(user_follow)
        else:
            user.following_list.add(user_follow)
        user.save()
    following = user.following_list.all()
    posts = Post.objects.filter(user__in=following).order_by("-timestamp").all()
    content = paginator(posts, get_page(request))
    return render(request, "network/index.html", content)
