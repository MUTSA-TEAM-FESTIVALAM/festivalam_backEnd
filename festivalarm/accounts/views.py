from os import access
from urllib.request import HTTPRedirectHandler
from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
import requests
import json

from festivalapp.models import User, Post, Comment
from .tokens import *
from my_secrets import CLIENT_ID, REDIRECT_URI, SECRET_KEY

from django.contrib import auth
# from django.contrib.auth.models import User


class KakaoSignInView(View):
    def get(self, request):
        kakao_auth_api = 'https://kauth.kakao.com/oauth/authorize?response_type=code'
        
        return redirect(
            f'{kakao_auth_api}&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}'
        )

# csrf 해제
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


@method_decorator(csrf_exempt, name='dispatch')
class KakaoSignInCallBackView(View):
    def post(self, request):

        # --- 인가코드 가져오기 --- #
        data = json.loads(request.body)
        code = data.get('code', None)

        # --- 카카오 토큰 받아오기 --- #
        token_request = requests.post(
            f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&code={code}"
        )
        token_json = token_request.json()
        access_token = token_json.get("access_token")
        refresh_token = token_json.get("refresh_token")
        
        # --- 사용자 정보 받아오기 --- #
        profile_request = requests.post(
            "https://kapi.kakao.com/v2/user/me", headers={"Authorization": f"Bearer {access_token}"}
        )
        profile_json = profile_request.json()

        kakao_id = profile_json.get('id')
        nickname = profile_json.get("properties")["nickname"]
        email = profile_json.get("kakao_account")["email"]
        
        # DB에 사용자 정보가 있는경우
        if User.objects.filter(kakao_id=kakao_id).exists():
            u = User.objects.get(kakao_id=kakao_id)
            u.email = email                      # 이메일이 바뀔수도 있어서 넣은건데 이 경우를 고려해야되나..
            u.access_token = access_token        # DB 리뉴얼 후 삭제
            u.refresh_token = refresh_token      # DB 리뉴얼 후 삭제
            u.save()

        # 회원가입인 경우
        else:
            User(
                kakao_id=kakao_id,
                username = nickname,
                email = email,
                access_token = access_token,        # DB 리뉴얼 후 삭제
                refresh_token = refresh_token,      # DB 리뉴얼 후 삭제
            ).save()


        return JsonResponse({"kakao_id":kakao_id, "access_token":access_token, "refresh_token":refresh_token})

# 로그아웃
# token을 프론트에서 받아와서 쓴다면 수정 필요
@method_decorator(csrf_exempt, name='dispatch')
class KakaoLogoutView(View):
    def post(self, request, kakao_id):

        # ~ 22.12.27 : DB에서 토큰을 끌어오는 방법이고
        # 22.12.28 ~ : 프론트에서 토큰을 받아서 사용
        data = json.loads(request.body)
        access_token = data.get('access_token', None)
        
        logout_request = requests.post(
            "https://kapi.kakao.com/v1/user/logout", headers={"Authorization": f"Bearer {access_token}"}
        )
        logout_info = logout_request.json()

        return JsonResponse({"id" : logout_info , "status": 'logout'})



# 연결끊기
@method_decorator(csrf_exempt, name='dispatch')
class KakaoUnlinkView(View):
    def post(self, request, kakao_id):
    
        # ~ 22.12.27 : DB에서 토큰을 끌어오는 방법이고
        # 22.12.28 ~ : 프론트에서 토큰을 받아서 사용
        data = json.loads(request.body)
        access_token = data.get('access_token', None)
        
        unlink_request = requests.post(
            f"https://kapi.kakao.com/v1/user/unlink?targetarget_id_type={'kakao_id'}&target_id={kakao_id}", headers={"Authorization": f"Bearer {access_token}"}
        )
        unlink_response = unlink_request.json()
        
        return JsonResponse({"id" : unlink_response , "status": 'unlink'})


# --- 마이페이지 --- #
# 사용자 정보를 어떻게 조회?
# 현재는 DB에 있는 사용자 정보를 끌어와서 프론트에 전달.. 이게 맞지
# kakao_id를 url로 받는게 아니라 request.body로 받아야되나
@method_decorator(csrf_exempt, name='dispatch')
class KakaoUserProfileView(View):
    def get(self, request, kakao_id):
        
        # 유저의 모든 정보 #
        user_queryset = User.objects.filter(kakao_id=kakao_id)
        user_json = json.loads(serializers.serialize('json', user_queryset))

        # user_queryset에서 username 뽑아오기
        username = user_queryset.values('username')[0]['username']
        print(username)

        # Post중 User의 username으로 작성된 post 가져오기
        user_post_queryset = Post.objects.filter(author__username=username)
        user_post_json = json.loads(serializers.serialize('json', user_post_queryset))
        
        # Comment중 User의 username으로 작성된 comment 가져오기
        user_comment_queryset = Comment.objects.filter(author__username=username)
        user_comment_json = json.loads(serializers.serialize('json', user_comment_queryset))

        return JsonResponse({"user_profile" : user_json, 'user_post': user_post_json, 'user_comment': user_comment_json })
    
    def post(self, request, kakao_id):
        data = json.loads(request.body)
        new_name = data.get('name', None)

        u = User.objects.get(kakao_id=kakao_id)
        u.username = new_name
        u.save()

        user_queryset = User.objects.filter(kakao_id=kakao_id)
        user_json = json.loads(serializers.serialize('json', user_queryset))

        username = user_queryset.values('username')[0]['username']
        print(new_name)

        return JsonResponse({"nickname" : username})


# --- access_token 기간 만료시 access/refresh token 갱신 --- #
class KaKaoTokenUpdateView(View):
    def get(self, request):

        # ~ 22.12.27 : 프론트에서 kakao_id를 request로 넘겨 받아서 그 아이디로 DB에서 refresh_token을 찾는 방법 사용
        # 22.12.28 ~ : token을 프론트로 넘겨주면 처음부터 refresh_token을 받으면 됨
        data = json.loads(request.body)
        refresh_token = data.get('refresh_token', None)
        

        token_request = requests.post(
            f"https://kauth.kakao.com/oauth/token?grant_type={'refresh_token'}&client_id={CLIENT_ID}&refresh_token={refresh_token}",
        )
        token_json = token_request.json()

        access_token = token_json.get("access_token")
        refresh_token = token_json.get("refresh_token")

        return JsonResponse({"access_token" : access_token, 'refresh_token': refresh_token})


@method_decorator(csrf_exempt, name='dispatch')
def PostDelete(request, kakao_id, post_id):
    if request.method == 'POST':
        post = Post.objects.filter(pk=post_id)          # queryset = get_object_or_404(Post, pk=post_id)  # get_object_or_404롤 객체 받아오면 serialize가 안되는 이유는?
        post.delete()

        # 유저의 모든 정보 #
        user_queryset = User.objects.filter(kakao_id=kakao_id)
        user_json = json.loads(serializers.serialize('json', user_queryset))

        # user_queryset에서 username 뽑아오기
        username = user_queryset.values('username')[0]['username']

        # Post중 User의 username으로 작성된 post 가져오기
        user_post_queryset = Post.objects.filter(author__username=username)
        user_post_json = json.loads(serializers.serialize('json', user_post_queryset))

        return JsonResponse({"user_post" : user_post_json})

    else:
        return JsonResponse({"status" : "GET 요청 받았음 / post로 보내"})
    # return redirect('post_list')


@method_decorator(csrf_exempt, name='dispatch')
def CommentDelete(request, kakao_id, comment_id):
    if request.method == 'POST':
        comment = Comment.objects.filter(pk=comment_id)          # queryset = get_object_or_404(Post, pk=post_id)  # get_object_or_404롤 객체 받아오면 serialize가 안되는 이유는?
        comment.delete()

        # 유저의 모든 정보 #
        user_queryset = User.objects.filter(kakao_id=kakao_id)
        user_json = json.loads(serializers.serialize('json', user_queryset))

        # user_queryset에서 username 뽑아오기
        username = user_queryset.values('username')[0]['username']

        # Post중 User의 username으로 작성된 post 가져오기
        user_comment_queryset = Comment.objects.filter(author__username=username)
        user_comment_json = json.loads(serializers.serialize('json', user_comment_queryset))

        return JsonResponse({"user_comment" : user_comment_json})

    else:
        return JsonResponse({"status" : "GET 요청 받았음 / post로 보내"})
    # return redirect('post_list')

    
