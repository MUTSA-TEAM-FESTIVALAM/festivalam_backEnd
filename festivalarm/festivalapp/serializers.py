from rest_framework import serializers
from .models import OptionCount, User, Festival, Place, Post, Comment, Option,OptionCount,FestivalImage,PostImage

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model= User
        fields=['id','kakao_id','email','username','access_token','refresh_token','password']

# class ProfileSerializer(serializers.ModelSerializer):
#     user=UserSerializer(read_only=True)
    
#     class Meta:
#         model= Profile
#         fields=['user','nickname']

class FestivalImageSerializer(serializers.ModelSerializer):
    class Meta:
        model= FestivalImage
        fields=['id','festival_id','image_url']
        
class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model= PostImage
        fields=['id','post_id','image_url']


class FestivalInfoSerializer(serializers.ModelSerializer):
    festival_images = FestivalImageSerializer(many=True, read_only=True)
    class Meta:
        model= Festival
        fields=['id','title','place', 'time_start', 'time_end','ticket_open','ticket_link','festival_images','lineup','hits']

class FestivalSaveSerializer(serializers.ModelSerializer):

    class Meta:
        model= Festival
        fields=['id','title','place', 'time_start', 'time_end','ticket_open','ticket_link','lineup','hits']

class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model= Place
        fields=['id','festival','name','name_adress','land_adress']
        
class PostSerializer(serializers.ModelSerializer):
    author=UserSerializer(read_only=True)
    post_images = PostImageSerializer(many=True, read_only=True)
    class Meta:
        model= Post
        fields=['id','author','festival_id','title','body','post_images','date','hits','category']

# class PostCreateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model= Post
#         fields=['title','body','image','category']
        
class CommentSerializer(serializers.ModelSerializer):
    author=UserSerializer(read_only=True)
    class Meta:
        model= Comment
        fields=['id','author','post_id','comment','date']
        
class OptionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model= Option
        fields=['id','festival_id','option1','option2','option3','option4','option5','option6']
          
class OptionCountSerializer(serializers.ModelSerializer):
    class Meta:
        model= OptionCount
        fields=['festival_id','option1','option2','option3','option4','option5','option6']
        
