
from django.shortcuts import render,redirect
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from .models import OptionCount, User, Festival, Post, Comment, Option
from .serializers import OptionCountSerializer, UserSerializer, FestivalInfoSerializer,FestivalImageSerializer,FestivalSaveSerializer, PostSerializer,PostImageSerializer, CommentSerializer, OptionSerializer
from .forms import PostForm,CommentForm
from rest_framework.renderers import TemplateHTMLRenderer

from festivalapp import ft_s3



#from festivalarm.festivalapp import serializers
# Create your views here. 

class FestivalsAPI(APIView):        # 페스티벌 전체목록
                                    #127.0.0.1:8000/festivalapp/festivals
    def get(self,request):          # 정보가져오기
        festivals= Festival.objects.all()
        serializer = FestivalInfoSerializer(festivals,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    def post(self,request):
        for i in range(len(request.data)):
            image_json_arr = request.data[i]["festival_images"]
            festival_data = request.data[i].pop("festival_images")
            festival_serializer = FestivalSaveSerializer(data = festival_data)
            if(festival_serializer.is_valid()):
                festival = festival_serializer.save()
                for k in range(len(image_json_arr)):
                    image_json_arr[k].append({"festival_id" : festival["id"]})
                    image_serializer = FestivalImageSerializer(image_json_arr[k])
                    if(image_serializer.is_valid()):
                        image_serializer.save()
                    else :
                        return Response(festival_serializer.errors ,status=status.HTTP_400_BAD_REQUEST)
                return Response(festival_serializer.data ,status=200)
            return Response(festival_serializer.errors ,status=status.HTTP_400_BAD_REQUEST)
 
    
class FestivalAPI(APIView):        # 페스티벌 상세목록
                                    #127.0.0.1:8000/festivalapp/festival/<int:festival_id> 
    def get(self,request,festival_id):     # 정보가져오기
        festival= get_object_or_404(Festival,id=festival_id)
        serializer = FestivalInfoSerializer(festival)
        return Response(serializer.data,status=status.HTTP_200_OK)

class PostsAPI(APIView):        # 게시글 전체목록
    def get(self,request):          # 정보가져오기
        posts= Post.objects.all()
        serializer = PostSerializer(posts,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def post(self,request): # request에 카테고리도 포함하여 포스트    # 넘겨줘야하는 값(kakao_id, title, body, image, category)
        user=get_object_or_404(User,kakao_id=request.data["kakao_id"])
        if request.data["festival_id"] != None :
            festival=get_object_or_404(Festival,id=request.data["festival_id"])
            serializer = PostSerializer(data= request.data,author=user,festival=festival,category=request.data["category"],hits=0)
        else :
            serializer = PostSerializer(data= request.data,author=user,category=request.data["category"],hits=0)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class CategoryPostsAPI(APIView):           # 글 게시판별 후기,
    def get(self,request):         # 글 목록 가져오기 (게시판별로) request.data에 category속성 안에 "review","friend","info","ticket"
        posts= Post.objects.filter(category=request.data["category"]) # 게시판 카테고리 별로 필터링해서 가져오기
        serializer = PostSerializer(posts,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
class PostAPI(APIView):           # 글 상세
    def get(self,request,post_id):         # 글 상세목록 가져오기 (id)
        post= get_object_or_404(Post,id=post_id) 
        serializer = PostSerializer(post)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def put(self, request, post_id):# 글 수정
        post=get_object_or_404(Post,id=post_id)
        serializer = PostSerializer(post, data=request.data) 
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id):# 글 삭제
        post=get_object_or_404(Post,id=post_id)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)    
    
class CommentsAPI(APIView):#게시글에적힌댓글 전체 127.0.0.1:8000/festivalapp/post/<int:post_id>/comments
    def get(self,request,post_id):          # 게시글에 적힌 댓글 전부 가져오기
        post=get_object_or_404(Post,id=post_id)
        comments= Comment.objects.filter(post=post)
        serializer = CommentSerializer(comments,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def post(self,request,post_id): # 게시글에 댓글 작성   # request.data에 넘겨줘야하는 값(kakao_id, comment)
        author=get_object_or_404(User,kakao_id=request.data["kakao_id"])
        post=get_object_or_404(Post,id=request.data["post_id"])
        serializer = CommentSerializer(comment=request.data["comment"],author=author,post=post)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentAPI(APIView):# 댓글 상세127.0.0.1:8000/festivalapp/comment/<int:comment_id>
    def put(self, request, comment_id):# 댓글 수정  request.data에 넘겨줘야하는 값(comment)
        oldcomment=get_object_or_404(Comment,id=comment_id)
        serializer = CommentSerializer(oldcomment, comment=request.data["comment"]) 
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, comment_id):# 댓글 삭제
        comment=get_object_or_404(Comment,id=comment_id)
        comment.delete()                                            
        return Response(status=status.HTTP_204_NO_CONTENT)    


class LikeAPI(APIView): # 127.0.0.1:8000/festivalapp/festival/<int:festiaval_id>/likes
    def post(self,request,festival_id):         # 페스티벌 좋아요 
        #만약 request안에 user을 담지 못할 시 이게 안될 시 아래 주석으로 실행 
        if request.user.is_authenticated:
            festival= get_object_or_404(Festival,id=festival_id) 
            if request.user in festival.likes.all():
               festival.likes.remove(request.user)
            else:
              festival.likes.add(request.user)
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    # 이 아래걸로 실행해보기
    # def post(self,request,festival_id):  # request.data 안에 kakao_id 넣기
    #     if request.data["kakao_id"] is None :
    #         return Response(status=status.HTTP_401_UNAUTHORIZED)
    #     user = get_object_or_404(User,kakao_id = request.data["kakao_id"])
    #     festival= get_object_or_404(Festival,id=festival_id) 
    #     if user in festival.likes.all():
    #        festival.likes.remove(user)
    #     else:
    #        festival.likes.add(user)
    #     return Response(status=status.HTTP_201_CREATED)
    
class OptionAPI(APIView): # 127.0.0.1:8000/festivalapp/festival/<int:festiaval_id>/thema
    # def get(self,request,festival_id):     # 페스티벌에 내가 입력한 후기 가져오기 fid 만 보내기
    #     festival= get_object_or_404(Festival,id=festival_id)
    #     serializer = Option.objects.filter(festival=festival,user=request.user)
    #     return Response(serializer.data,status=status.HTTP_200_OK)
    
    def post(self,request,festival_id): # 인자로 fid 받고 request에 옵션1~6포함 +[kakao_id는 request.data 안에]
        festival=get_object_or_404(Festival,id=festival_id)
        user=get_object_or_404(User,kakao_id=request.data["kakao_id"])
        serializer = OptionSerializer(data= request.data,user=user,festival=festival)
        if serializer.is_valid():
            serializer.save()
            option_count=get_object_or_404(OptionCount,festival=festival)
            num=option_count.check_num
            countoption1 = (option_count.option1 * num + serializer.option1)/ (option_count.check_num +1)
            countoption3 = (option_count.option3 * num + serializer.option3)/ (option_count.check_num +1)
            countoption2 = (option_count.option2 * num + serializer.option2)/ (option_count.check_num +1)
            countoption4 = (option_count.option4 * num + serializer.option4)/ (option_count.check_num +1)
            countoption5 = (option_count.option5 * num + serializer.option5)/ (option_count.check_num +1)
            countoption6 = (option_count.option6 * num + serializer.option6)/ (option_count.check_num +1)
            num += 1
            countserializer=OptionCountSerializer(option_count,check_num=num,option1=countoption1,option2=countoption2,option3=countoption3,option4=countoption4,option5=countoption5,option6=countoption6)
            countserializer.save() # 여기서 생각해보니 처음붵 그냥 option_count를 수정해서 save해도 되지않았을까???? 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request,fid):#  인자로 fid 받음 + request.data 안에kakao_id
        festival=get_object_or_404(Festival,id=fid)
        user=get_object_or_404(User,kakao_id=request.data["kakao_id"])
        option=get_object_or_404(Option,festival=festival,user=user)
        
        option_count=get_object_or_404(OptionCount,festival=festival)
        num=option_count.check_num
        countoption1 = (option_count.option1 * num - option.option1)/ (option_count.check_num -1)
        countoption3 = (option_count.option3 * num - option.option3)/ (option_count.check_num -1)
        countoption2 = (option_count.option2 * num - option.option2)/ (option_count.check_num -1)
        countoption4 = (option_count.option4 * num - option.option4)/ (option_count.check_num -1)
        countoption5 = (option_count.option5 * num - option.option5)/ (option_count.check_num -1)
        countoption6 = (option_count.option6 * num - option.option6)/ (option_count.check_num -1)
        num -= 1
        countserializer=OptionCountSerializer(option_count,check_num=num,option1=countoption1,option2=countoption2,option3=countoption3,option4=countoption4,option5=countoption5,option6=countoption6)
        countserializer.save()
            
        option.delete()                                            
        return Response(status=status.HTTP_204_NO_CONTENT)    


    
class CountOptionAPI(APIView): #127.0.0.1:8000/festivalapp/festival/<int:festiaval_id>/total_thema
    def get(self,request,festival_id):     
        festival=get_object_or_404(Festival,id=festival_id)
        option_count= get_object_or_404(OptionCount,festival=festival)
        serializer = FestivalSerializer(option_count)
        return Response(serializer.data,status=status.HTTP_200_OK)
    

class MyPostAPI(APIView):# 127.0.0.1:8000/festivalapp/mypage/posts    request.data에 kakao_id보내기
    def get(self,request):     # request.data안에 kakao_id넣기
        user= get_object_or_404(kakao_id=request.data["kakao_id"])
        myposts=Post.objects.filter(user=user)
        serializer = PostSerializer(myposts,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    
class MyCommentAPI(APIView):# 127.0.0.1:8000/festivalapp/mypage/comments    request.data에 kakao_id보내기
    def get(self,request):    # request.data안에 kakao_id넣기
        user= get_object_or_404(kakao_id=request.data["kakao_id"]) 
        mycomments=Comment.objects.filter(user=user)
        serializer = CommentSerializer(mycomments,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    
class MyLikeAPI(APIView):# 127.0.0.1:8000/festivalapp/mypage/likes      request.data에 kakao_id보내기
    def get(self,request):     
        user= get_object_or_404(kakao_id=request.data["kakao_id"])
        mylikes=user.like.all()
        serializer = CommentSerializer(mylikes,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    

class SearchPostTitleAPI(APIView): # 127.0.0.1:8000/festivalapp/search/post/
    def get(self,request):       # search라는 매개변수로 검색할 내용을 받음 request.data 안에 search로 주기
        posts=Post.objects.filter(title__icontains = request.data["search"]) | Post.objects.filter(author__icontains = request.data["search"])
                                                                             # __contains ==>__앞에 있는 속성안에 뒤에오는 내용이 포함된것을 필터링 
                                                                             # __icontains ==> 대소문자 구별 x
                                                                             # |, & 는 Or, And표현
        serializer = PostSerializer(posts,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
# class SearchPostNameAPI(APIview):
#     def get(self,request,search):       # search라는 매개변수로 검색할 내용을 받음
#         posts=Post.objects.filter(nickname__contains = search) #?? nickname 대신에 뭐가와야할까?
#         serializer = PostSerializer(posts,many=True)
#         return Response(serializer.data,status=status.HTTP_200_OK)
    

class SearchFestivalTitleAPI(APIView):
    def get(self,request):       # search라는 매개변수로 검색할 내용을 받음 request.data 안에 search로 주기
        festivals=Festival.objects.filter(title__contains =request.data["search"]) | Festival.objects.filter(lineup__contains =request.data["search"])
        serializer = FestivalSerializer(festivals,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
#class SearchOptionAPI(APIview):









