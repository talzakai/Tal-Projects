from turtle import pos
from django.shortcuts import redirect, render
from . models import Profile, Group, Post, Comment
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.core.paginator import Paginator

# Create your views here.

def landing(request):
    return render(request,'socialApp/landing.html',{})

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except:
            return render(request,'socialApp/login.html',{"error":"Username Not Found"})

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            return render(request,'socialApp/login.html',{"error":"Username or Password incorrect"}) 
    return render(request,'socialApp/login.html',{})

def logout_user(request):
    logout(request)
    return redirect('landing')

def signup_user(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if (request.POST['firstName'] != '' and request.POST['lastName'] != '' and request.POST['city'] != '' and
            request.POST['dob'] != '' and 'relationship' in request.POST):

            if form.is_valid():
                form.save()
                username = request.POST['username']
                password = request.POST['password1']
                user = authenticate(username=username,password=password)

                Profile.objects.create(
                    user=user,
                    first_name=request.POST['firstName'],
                    last_name=request.POST['lastName'],
                    city = request.POST['city'],
                    dob = request.POST['dob'],
                    imageUrl = request.POST['imageUrl'],
                    relationship = request.POST['relationship']
                )
                return redirect('login')
        else:
            return render(request,'socialApp/signup.html',{"form":form,"error":"All fields expect imageUrl must be completed"})
    return render(request,'socialApp/signup.html',{"form":form})

@login_required(login_url='landing')
def home(request):
    profile = request.user.profile
    friends = request.user.friends.all()

    groups = profile.usersGroup.all() | profile.ownerGroup.all()
    groups = groups.distinct().order_by("name")

    posts = Post.objects.filter(userPost = None)
    for friend in friends:
        temp = Post.objects.filter(
            Q(userPost = friend) &
            Q(group = None)).order_by("-created")
        posts = posts | temp
    for group in groups:
        temp = Post.objects.filter(group = group).order_by("-created")
        posts = posts | temp
    posts = posts.order_by("-created").distinct()
    p = request.GET.get('p') if request.GET.get('p') != None else None
    page_object = Paginator(posts, 2)
    try:
        context = page_object.page(int(p)) if p != None else page_object.page(1)
    except:
        context = page_object.page(page_object.num_pages - 1) if page_object.num_pages > 1 else page_object.page(1)
 
    return render(request,'socialApp/home.html',{"profile":profile, "posts":posts, "groups":groups, "friends":friends, "page_object":page_object, "context": context})

@login_required(login_url='landing')
def profile(request, username):
    profile = User.objects.get(username = username).profile
    friends = profile.user.friends.all()
    posts = profile.post.all().order_by("-created")

    groups = profile.usersGroup.all() | profile.ownerGroup.all()
    groups = groups.distinct().order_by("name")

    p = request.GET.get('p') if request.GET.get('p') != None else None
    page_object = Paginator(posts, 2)
    try:
        context = page_object.page(int(p)) if p != None else page_object.page(1)
    except:
        context = page_object.page(page_object.num_pages - 1) if page_object.num_pages > 1 else page_object.page(1)
    return render(request,'socialApp/profile.html',{"profile":profile, "groups":groups, "friends":friends, "posts":posts, "page_object":page_object, "context": context})

@login_required(login_url='landing')
def edit_profile(request, username):
    if request.user.username != username:
        return redirect('home')

    profile = request.user.profile
    if request.method == 'POST':
        profile.first_name=request.POST['firstName']
        profile.last_name=request.POST['lastName']
        profile.city = request.POST['city']
        profile.dob = request.POST['dob']
        profile.imageUrl = request.POST['imageUrl']
        profile.relationship = request.POST['relationship']
        profile.save()
        return redirect('profile', username)
    return render(request,'socialApp/edit_profile.html',{})

@login_required(login_url='landing')
def remove_user(request, username):
    if request.user.username != username:
        return redirect('home')
        
    if request.method == 'POST':
        request.user.delete()
        return redirect('landing')
    return render(request,'socialApp/delete_user.html',{})

@login_required(login_url='landing')
def add_friend(request, username):
    profile = request.user.profile
    friend = User.objects.get(username = username)
    profile.friends.add(friend)
    friend.profile.friends.add(profile.user)
    return redirect('profile', username)

@login_required(login_url='landing')
def remove_friend(request, username):
    profile = request.user.profile
    friend = User.objects.get(username = username)
    profile.friends.remove(friend)
    friend.profile.friends.remove(profile.user)
    return redirect('profile', username)

@login_required(login_url='landing')
def add_like(request, id):
    profile = request.user.profile
    post = Post.objects.get(id = id)
    post.likes.add(profile)
    return redirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='landing')
def remove_like(request, id):
    profile = request.user.profile
    post = Post.objects.get(id = id)
    post.likes.remove(profile)
    return redirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='landing')
def post(request, id):
    post = Post.objects.get(id = id)
    profile = post.userPost
    comments = post.comment.all().order_by("-created")
    p = request.GET.get('p') if request.GET.get('p') != None else None
    page_object = Paginator(comments, 3)
    try:
        context = page_object.page(int(p)) if p != None else page_object.page(1)
    except:
        context = page_object.page(page_object.num_pages - 1) if page_object.num_pages > 1 else page_object.page(1)
    return render(request,'socialApp/post.html',{"profile":profile, "post":post, "comments":comments, "page_object":page_object, "context": context})

@login_required(login_url='landing')
def add_post(request):
    profile = request.user.profile
    if request.method == "POST":
        Post.objects.create(
        userPost=profile,
        body = request.POST['body'],
        imageUrl = request.POST['imageUrl']
        )
        return redirect('profile', profile.user.username)
    return render(request,'socialApp/add_post.html',{})

@login_required(login_url='landing')
def edit_post(request, id):
    post = Post.objects.get(id = id)
    if request.user.profile != post.userPost:
        return redirect('home')
        
    if request.method == 'POST':
        post.body=request.POST['body']
        post.imageUrl = request.POST['imageUrl']
        post.save()
        return redirect('post', id)
    return render(request,'socialApp/edit_post.html',{"post":post})

@login_required(login_url='landing')
def remove_post(request, id):
    post = Post.objects.get(id = id)
    if request.user.profile != post.userPost:
        return redirect('home')
        
    if request.method == 'POST':
        post.delete()
        return redirect('home')
    return render(request,'socialApp/delete_post.html',{"post":post})

@login_required(login_url='landing')
def add_comment(request, id):
    profile = request.user.profile
    post = Post.objects.get(id = id)
    if request.POST['body'] != "":
        Comment.objects.create(
            userComment=profile,
            post = post,
            body = request.POST['body']
        )
    return redirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='landing')
def edit_comment(request, id):
    comment = Comment.objects.get(id = id)
    if request.user.profile != comment.userComment:
        return redirect('home')
        
    if request.method == 'POST':
        comment.body=request.POST['body']
        comment.save()
        return redirect('post', comment.post.id)

    return render(request,'socialApp/edit_comment.html',{"comment":comment})
      
@login_required(login_url='landing')
def remove_comment(request, id):
    comment = Comment.objects.get(id = id)
    if request.user.profile != comment.userComment and request.user.profile != comment.post.userPost:
        return redirect('home')
        
    comment.delete()
    return redirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='landing')
def group(request, id):
    profile = request.user.profile
    group = Group.objects.get(id=id)
    posts = group.post.all().order_by("-created")
    
    p = request.GET.get('p') if request.GET.get('p') != None else None
    page_object = Paginator(posts, 2)
    try:
        context = page_object.page(int(p)) if p != None else page_object.page(1)
    except:
        context = page_object.page(page_object.num_pages - 1) if page_object.num_pages > 1 else page_object.page(1)
 
    return render(request,'socialApp/group.html',{"profile":profile, "group":group, "posts":posts, "page_object":page_object, "context": context})

@login_required(login_url='landing')
def add_group(request):
    profile = request.user.profile
    if request.method == "POST":
        Group.objects.create(
        name = request.POST['name'],
        description = request.POST['description'],
        owner = profile,
        )
        return redirect('home')
    return render(request,'socialApp/add_group.html',{})

@login_required(login_url='landing')
def edit_group(request, id):
    group = Group.objects.get(id = id)
    if request.user.profile != group.owner:
        return redirect('home')
        
    if request.method == 'POST':
        group.name=request.POST['name']
        group.description = request.POST['description']
        group.save()
        return redirect('group', id)
 
    return render(request,'socialApp/edit_group.html',{"group":group})

@login_required(login_url='landing')
def remove_group(request, id):
    group = Group.objects.get(id = id)
    if request.user.profile != group.owner:
        return redirect('home')
        
    if request.method == 'POST':
        group.delete()
        return redirect('home')
 
    return render(request,'socialApp/delete_group.html',{"group":group})

@login_required(login_url='landing')
def join_group(request, id):
    profile = request.user.profile
    group = Group.objects.get(id = id)
    group.users.add(profile)
    return redirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='landing')
def leave_group(request, id):
    profile = request.user.profile
    group = Group.objects.get(id = id)
    group.users.remove(profile)
    return redirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='landing')
def kick_group(request, id, username):
    profile = request.user.profile
    group = Group.objects.get(id = id)
    if group.owner != profile:
        return redirect(request.META.get('HTTP_REFERER'))

    userToKick = User.objects.get(username = username).profile
    group.users.remove(userToKick)
    return redirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='landing')
def remove_post_group(request, id):
    post = Post.objects.get(id = id)
    if request.user.profile != post.group.owner:
        return redirect('home')
        
    if request.method == 'POST':
        post.delete()
        return redirect('home')
    return render(request,'socialApp/delete_post.html',{"post":post})

@login_required(login_url='landing')
def add_post_group(request, id):
    profile = request.user.profile
    group = Group.objects.get(id = id)
    if request.method == "POST":
        Post.objects.create(
        userPost=profile,
        group=group,
        body = request.POST['body'],
        imageUrl = request.POST['imageUrl']
        )
        return redirect('group', id)
    return render(request,'socialApp/add_post.html',{})

@login_required(login_url='landing')
def remove_comment_group(request, id):
    comment = Comment.objects.get(id = id)
    if request.user.profile != comment.post.group.owner:
        return redirect('home')
        
    comment.delete()
    return redirect(request.META.get('HTTP_REFERER'))


@login_required(login_url='landing')
def search(request):
    q = request.GET.get('q')
    profiles = Profile.objects.filter(
        Q(first_name__icontains=q) |
        Q(last_name__icontains=q)
    )
    groups = Group.objects.filter(name__icontains=q) 

    userGroups = request.user.profile.usersGroup.all() | request.user.profile.ownerGroup.all()
    userGroups = userGroups.distinct()

    friends = request.user.friends.all()
    posts = Post.objects.filter(
        Q(body__icontains=q) &
        Q(userPost = request.user.profile)).order_by("-created")
    for friend in friends:
        temp = Post.objects.filter(
            Q(userPost = friend) &
            Q(group = None) &
            Q(body__icontains=q)
        ).order_by("-created")
        posts = posts | temp
    for group in userGroups:
        temp = Post.objects.filter(
            Q(group = group) &
            Q(body__icontains=q)
            ).order_by("-created")
        posts = posts | temp
    posts = posts.order_by("-created").distinct()
    return render(request,'socialApp/search.html',{"profiles":profiles, "groups":groups, "posts":posts})