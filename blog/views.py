from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from blog.models import Post, Comment
from blog.forms import AuthForm, PostForm, CommentForm

from django.utils import timezone


def index(request):
    latest_post_list = Post.objects.order_by('-pub_date')
    is_logged_in = request.user.is_authenticated
    context = {'latest_post_list': latest_post_list, 'is_logged_in': is_logged_in}
    return render(request, 'blog/index.html', context)


# posts

def postDetail(request, post_id, error=None, comment_form_from_create=None):
    post = Post.objects.get(pk=post_id)
    comments = Comment.objects.filter(post=post_id)
    comment_form = CommentForm()
    is_logged_in = request.user.is_authenticated
    context = {'post': post, 'comments': comments, 'is_logged_in': is_logged_in, 'post_id': post_id}
    if error:
        context['error'] = error
    if comment_form_from_create:
        context['comment_form'] = comment_form_from_create
    else: context['comment_form'] = comment_form
    # if comment_form:
    #     context['comment_form'] = comment_form
    return render(request, 'blog/detail.html', context)

def postView(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.pub_date = timezone.now()
            post.save()
            return postDetail(request, post.id)
    else:
        form = PostForm()
    is_logged_in = request.user.is_authenticated
    return render(request, 'blog/create.html', {'form': form, 'is_logged_in': is_logged_in})

def deletePostView(request, post_id):
    if request.method == 'POST':
        post = Post.objects.get(pk=post_id)
        # should check if the post is the being deleted by the user who created it
        # if post.author == request.user:
        post.delete()
        return redirect('/')
        # return index(request)

        # else statement accompanying the strongly desired if statement from above
        # else:
        #     return postDetail(request=request, post_id=post_id, error='This is not your post !')
    else:
        return postDetail(request=request, post_id=post_id, error='Incorrect method !')

# profile

def profileView(request, user_id):
    if request.method == 'GET':
        # this is unsafe as user_id is a query parameter (which may be tampered with), not the user from session
        # should be: user = request.user
        user = User.objects.get(pk=user_id)

        # this is unsafe because it gets all the user's posts, which can be potentially a huge number of items
        posts = Post.objects.filter(author=user)

        is_logged_in = request.user.is_authenticated
        return render(request, 'blog/profile.html', {'username': user.username, 'posts': posts, 'date_joined': user.date_joined, 'id': user_id, 'is_logged_in': is_logged_in})
    else:
        return render('/')

def profileDeleteView(request, user_id):
    # very dangerous to use user_id query parameter and not checking the session
    # because potentially any user may delete any account
    if request.method == 'POST':
        # if user_id == request.user
        User.objects.get(pk=user_id).delete()
    return redirect('/')


# comments
def createCommentView(request):
    post_id = request.POST['post_id']
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = Post.objects.get(pk=post_id)
            comment.pub_date = timezone.now()
            comment.save()
            return redirect('/post/%s/' % post_id)
        else:
            return postDetail(request=request, post_id=post_id, comment_form_from_create=form)
    else:
        return postDetail(request=request, post_id=post_id, error='Incorrect method !')

def deleteCommentView(request):
    post_id = request.POST['post_id']
    if request.method == 'POST':
        comment = Comment.objects.get(pk=request.POST['comment_id'])
        if comment.author == request.user:
            comment.delete()
            # redirect back
            return redirect('/post/%s/' % post_id)
            # return postDetail(request=request, post_id=post_id)
        else:
            return postDetail(request=request, post_id=post_id, error='This is not your comment !')
    else:
        return postDetail(request=request, post_id=post_id, error='Incorrect method !')

# auth views

def signupView(request):
    if request.method == 'POST':
        form = AuthForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            if User.objects.filter(username=username).exists():
                return render(request, 'blog/auth.html', {'error': 'A user with this username already exists', 'form': form, 'auth_type': 'signup'})
            else:
                user = User.objects.create_user(username=username, password=password)
                user.save()
                login(request, user)
                return redirect('/')
    else:
        form = AuthForm()
    return render(request, 'blog/auth.html', {'form': form, 'auth_type': 'signup'})

def loginView(request):
    if request.method == 'POST':
        form = AuthForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                return render(request, 'blog/auth.html', {'error': 'Incorrect username or password','form': form, 'auth_type': 'login'})
    else:
        form = AuthForm()
    return render(request, 'blog/auth.html', {'form': form, 'auth_type': 'login'})

def logoutView(request):
    logout(request)
    return redirect('/')
