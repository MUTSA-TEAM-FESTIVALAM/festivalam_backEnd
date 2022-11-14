from django.urls import path
from . import views

urlpatterns = [
    path('festivals/', views.FestivalsAPI.as_view()),
    path('festival/<int:festival_id>', views.FestivalAPI.as_view()),
    path('festival/<int:festival_id>/likes', views.LikeAPI.as_view()),
    path('festival/<int:festival_id>/thema', views.OptionAPI.as_view()),
    path('festival/<int:festival_id>/total_thema', views.CountOptionAPI.as_view()),
    path('posts/', views.PostsAPI.as_view()),
    path('post/<int:post_id>', views.PostAPI.as_view()),
    path('post/<int:post_id>/comments', views.CommentsAPI.as_view()),
    path('comment/<int:comment_id>', views.CommentAPI.as_view()),
    path('mypage/posts/', views.MyPostAPI.as_view()),
    path('mypage/comments/', views.MyCommentAPI.as_view()),
    path('mypage/likes/', views.MyLikeAPI.as_view()),
    path('search/post/', views.SearchPostTitleAPI.as_view()),
    path('search/festival/', views.SearchFestivalTitleAPI.as_view()),
]