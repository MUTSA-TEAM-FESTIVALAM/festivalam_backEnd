from os import access
from urllib.request import HTTPRedirectHandler
from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
import requests
import json
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
#permission_classes = (IsAuthenticated,) #헤더인증된사람만 볼수있는 class설정 

from festivalapp.models import User, Post, Comment
from .tokens import *
from my_secrets import CLIENT_ID, REDIRECT_URI, SECRET_KEY, JWT_ALGORITHM

from django.contrib import auth
# from django.contrib.auth.models import User


# 인가코드 받아오는 메서드
class KakaoSignInView(View):
    def get(self, request):
        kakao_auth_api = 'https://kauth.kakao.com/oauth/authorize?response_type=code'
        
        return redirect(
            f'{kakao_auth_api}&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}'
        )

# csrf 해제
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


# 카카오 로그인
# 로그인 메서드에 보내는 token은 kakao_token이라서 기간이 만료되는 일은 없을것.
@method_decorator(csrf_exempt, name='dispatch')
class KakaoSignInCallBackView(View):
    def post(self, request) :
        
        #--- 0. 프론트에서 jwt(인가코드)를 넘겨줌 ---#

        #--- 1. 넘어온 jwt토큰을 복호화 ---#
        token = request.GET.get('code')
        code = decode_token(token)
        
        #--- 1.5 if 복호화 성공하면 인가코드를 얻음 ---#
        # 여기서 에러나는 경우는 decode_token() 메서드의 문제
        
        
        #--- 2 인가코드로 kakao_access를 받아옴 ---#
        token_request = requests.post(
                f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&code={code}"
            )
        token_json = token_request.json()
        access_token = token_json.get("access_token")

        #--- 3. access_toekn을 통해 kakao에서 사용자 정보 받아오기  ---#
        profile_request = requests.post(
            "https://kapi.kakao.com/v2/user/me", headers={"Authorization": f"Bearer {access_token}"}
        )
        profile_json = profile_request.json()

        #--- 4. DB에 사용자 정보 중 해당 id가 있는지 확인 ---#
        if not User.objects.filter(kakao_id=profile_json.get('id')).exists():
            # DB에 사용자 정보가 없는경우 --> 회원가입
            user = User(
                kakao_id = profile_json.get('id'),
                username = profile_json.get("properties")["nickname"],
                email = profile_json.get("kakao_account")["email"],
            ).save()

        
        payload = {
            "subject" : profile_json.get('id')   # "subject" : kakao_id
        }

        #--- 5. 유저의 kakao_id를 이용하여 jwt_access/refresh 발급 ---#
        jwt_access_token = generate_token(payload, "access")
        jwt_refresh_token = generate_token(payload, "refresh")
        
        #--- 6. jwt_refresh_token은 DB에 저장 ---#
        User(
            refresh_token = jwt_refresh_token,
        ).save()

        #--- 7. jwt_access/refresh 를 return  ---#
        return JsonResponse({'access_token': jwt_access_token, 'refresh_token' : jwt_refresh_token}, status=201)


# --- 마이페이지 --- #
@method_decorator(csrf_exempt, name='dispatch')
class KakaoUserProfileView(View):
    def post(self, request):
        
        try : 
            #--- 1. jwt 토큰을 전달 받기  ---#
            jwt_token = request.headers.get('Authorization', None)
    
            #--- Decoding ---#
            temp = jwt_token.split(' ')
            decoded = decode_token(temp)
            result = decoded['subject'] # 디코딩이 제대로 됐다면 result = kakao_id
            

            #--- 2. access 토큰이 유효하다면
            if  User.objects.filter(kakao_id=result).exists():
                
                # 유저의 정보 뽑아오기
                user_queryset = User.objects.filter(kakao_id=result)        
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
                
                return JsonResponse({"user_profile" : user_json, 'user_post': user_post_json, 'user_comment': user_comment_json }, status = 200)
                
            #--- 3. access 토큰이 유요하지 않다면 ---#
            #   3-1) 사용자의 새로고침으로 인하여 access토큰이 만료
            #   3-2) access_token의 기간이 만료    
            else :
                
                #--- jwt_refresh 를 가져와서 ---#
                data = json.loads(request.body)
                refresh_token = data.get('refresh_token', None)
                         
                #--- 4. refresh의 유효성 검사(전달받은 refresh와 DB에 저장돼있는 refresh 를 비교) ---#
                # 4-1) 유효성 검사 통과 
                if User.objects.filter(refresh_token=refresh_token).exists():
                    user_queryset = User.objects.filter(refresh_token=refresh_token)
                    kakao_id = user_queryset.values('kakao_id')[0]['kakao_id']
                    
                    payload = {
                        "subject" : kakao_id,
                    }
                    
                    # jwt_access & refresh 재발급
                    jwt_access_token = generate_token(payload, "access")
                    jwt_refresh_token = generate_token(payload, "refresh")

                    return JsonResponse({"access_token":jwt_access_token, "refresh_token":jwt_refresh_token}, status = 200)
                
                # 4-2) 유효성 검사 실패
                else :
                    print("로그인을 다시 해주세요")
        
        except jwt.exceptions.DecodeError:
            return JsonResponse({'message' : 'INVALID TOKEN'}, status = 400)

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
    def post(self, request):
    
        # ~ 22.12.27 : DB에서 토큰을 끌어오는 방법이고
        # 22.12.28 ~ : 프론트에서 토큰을 받아서 사용
        #data = json.loads(request.body)
        #access_token = data.get('access_token', None)
        #kakao_id = User.objects.values('kakao_id')[0]['kakao_id']
        access_token = User.objects.values('kakao_access_token')[0]['kakao_access_token']

        requests.post(
            "https://kapi.kakao.com/v1/user/logout", headers={"Authorization": f"Bearer {access_token}"}
        )
        #unlink_response = unlink_request.json()
        
        return JsonResponse({"status": 'unlink'})
    
@method_decorator(csrf_exempt, name='dispatch')
class UpdateNickname(View):
       # 이름 수정
    def post(self, request):
        try : 
            # 프론트에서 토큰을 전달 받기 
            access_token = request.headers.get('Authorization', None)
            #만약 사용자의 새로고침으로 인하여 access토큰이 만료되었다면?
            if (len(access_token) == 6):
                data = json.loads(request.body)
                refresh_token = data.get('refresh_token', None)
                
                # 예비용으로 refresh_token을 받아서 실제 유저 DB에 저장되어 있는지 체크합니다. 
                if User.objects.filter(refresh_token=refresh_token).exists():
                    user_num = 1
                    user_queryset = User.objects.filter(refresh_token=refresh_token)
                    decoded_id = user_queryset.values('kakao_id')[0]['kakao_id']
                     
            else : 
                jwtq, jwt_token = access_token.split(' ')
                decoded = decode_token(jwt_token)
                decoded_id = decoded['subject']
                user_num = User.objects.filter(kakao_id=decoded_id).count() 
            # kakao_id = 전달받은 access_token을 복호화(jwt) 

            if(user_num > 0):
            # 유저의 모든 정보
                data = json.loads(request.body)
                new_name = data.get('name', None)
                
                user_queryset = User.objects.filter(kakao_id=decoded_id)
                user = User.objects.get(kakao_id=decoded_id)
                user.username = new_name
                user.save()
                return JsonResponse({'newname' : 'GOOD'}, status = 200)

        except jwt.exceptions.DecodeError:
            return JsonResponse({'message' : 'INVALID TOKEN'}, status = 400)


@method_decorator(csrf_exempt, name='dispatch')
# --- access_token 기간 만료시 access/refresh token 갱신 및 access_token 인증하는부분 --- #
class KaKaoTokenUpdateView(View):
    def post(self, request):
        
        #만약 access_token이 유저의 새로고침으로 인하여 날아갔다면?
        try:
            access_token = request.headers.get('Authorization', None)
            if (len(access_token) == 6):
                data = json.loads(request.body)
                refresh_token = data.get('refresh_token', None)
                
                #refresh_token을 받아서 실제 유저 DB에 저장되어 있는지 체크합니다. 
                if User.objects.filter(refresh_token=refresh_token).exists():
                    user_queryset = User.objects.filter(refresh_token=refresh_token)
                    kakao_id = user_queryset.values('kakao_id')[0]['kakao_id']
                    payload = {
                        "subject" : kakao_id,
                    }
                    # 유저의 jwt access_token 재발급
                    jwt_access_token = generate_token(payload, "access")
                    # 유저의 jwt refresh_token 재발급
                    jwt_refresh_token = generate_token(payload, "refresh")
                    # 유저의 refresh_token을 jwt를 통하여 암호화하여 return
                    
                    #유저에 refresh_token 다시 저장 
                    user = User.objects.get(refresh_token=refresh_token)
                    user.refresh_token = jwt_refresh_token
                    user.save()

                    #새로 발급한 access_token과 refresh_token을 다시 client에게 넘겨줍니다. 
                    return JsonResponse({"access_token":jwt_access_token, "refresh_token":jwt_refresh_token}, status = 200)
                
                #refresh 토큰도 존재하지 않다면 그것은 인증되지 않은 유저이므로, 400을 반환합니다. 
                else:
                    return JsonResponse({'message': 'INVALID TOKEN'}, status = 400)
            
            #만약 access_token이 존재한다면? 
            jwtq, jwt_token = access_token.split(' ')
            decoded = decode_token(jwt_token)
            kakao_id = decoded['subject']
            user_num = User.objects.filter(kakao_id=kakao_id).count() 
            if(user_num > 0):
                data = json.loads(request.body)
                refresh_token = data.get('refresh_token', None)
                return JsonResponse({"access_token":jwt_token, "refresh_token":refresh_token}, status = 200)

        #만약 decode가 안된다면?
        except jwt.exceptions.DecodeError:
            return JsonResponse({'message' : 'INVALID TOKEN'}, status = 400)
        #만약 유저가 존재하지 않다면?
        except User.DoesNotExist:
            return JsonResponse({'message' : 'INVALID USER'}, status = 400)
        


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

    