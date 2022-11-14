from django.urls import path
from . import views


urlpatterns = [
    path('kakao/login/', views.KakaoSignInView.as_view(), name='kakao_login'),
    path('kakao/callback/', views.KakaoSignInCallBackView.as_view(), name='kakao_callback'),
    path('kakao/user/<int:kakao_id>/logout/', views.KakaoLogoutView.as_view(), name='kakao_logout'),
    path('kakao/user/<int:kakao_id>/unlink/', views.KakaoUnlinkView.as_view(), name='kakao_unlink'),
    path('kakao/user/<int:kakao_id>/profile/', views.KakaoUserProfileView.as_view(), name='kakao_user'),
    path('kakao/user/<int:kakao_id>/post/delete/<int:post_id>/', views.PostDelete, name='user_post_delete'),
    path('kakao/user/<int:kakao_id>/comment/delete/<int:comment_id>/', views.CommentDelete, name='user_comment_delete'),
]

