from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('post/', views.postView, name='create'),
    path('post/<int:post_id>/', views.postDetail, name='detail'),
    path('post/<int:post_id>/delete/', views.deletePostView, name='delete'),
    path('profile/<int:user_id>', views.profileView, name='profile'),
    path('profile/<int:user_id>/delete', views.profileDeleteView, name='profile-delete'),
    path('comment/', views.createCommentView, name='comment-create'),
    path('comment/delete/', views.deleteCommentView, name='comment-delete'),
    path('signup/', views.signupView, name='signup'),
    path('logout/', views.logoutView, name='logout'),
    path('login/', views.loginView, name='login'),
]