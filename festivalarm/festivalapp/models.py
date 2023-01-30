from email.policy import default
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import CharField, DateField, ImageField, IntegerField
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    kakao_id = models.CharField(blank=True, max_length=100,unique=True)
    username = models.CharField(unique=True, null=True, max_length=100)
    email = models.EmailField(blank=True)    
    kakao_access_token = models.CharField(blank=True, max_length=100, null=True)
    refresh_token = models.CharField(blank=True, max_length=500, null=True)

    
    def __str__(self):
        return self.username



# # 페스티벌 장르 >>안하기로 결정
# class Genre(models.Model):
#     name = models.CharField(max_length=20)

#     def __str__(self):
#         return self.name


# 게시글 카테고리 >> 게시글 모델 여러개로 하자
# class Category(models.Model):
#     name = models.CharField(max_length=20)

#     def __str__(self):
#         return self.name


# 페스티벌
class Festival(models.Model):
    title = models.CharField(blank=True, max_length=1000)
    ticket_link = models.URLField(blank=True,max_length = 1000) 
    time_start = models.DateField(blank=True)
    time_end = models.DateField(blank=True)
    place = models.CharField(blank=True,max_length=1000)
    ticket_open = models.DateTimeField(blank=True,null=True)
    lineup = models.CharField(blank=True,max_length=1000)
    hits = models.IntegerField(blank=True,default=0)
    likes = models.ManyToManyField(User,related_name='like',blank=True)
    # genre_id = models.ForeignKey(
    #     Genre,
    #     on_delete = models.SET_NULL,
    #     null = True,
    #     related_name='festival_genre'
    # )

    def __str__(self):
        return self.title    


# festival:place = 1:1
# class Place(models.Model):
#     # festival의 place를 fk로
#     festival = models.ForeignKey(
#         Festival, 
#         on_delete=models.CASCADE, 
#         related_name='place_festsival'
#     )
#     # catetory = models.ForeignKey(
#     #     Category,
#     #     on_delete = models.SET_NULL,
#     #     null = True,
#     #     related_name='like_festsival'
#     # )
#     name = models.CharField(blank=True, max_length=20)
#     name_address = models.CharField(blank=True, max_length=20) # 도로명주소
#     land_address = models.CharField(blank=True, max_length=20) # 지번주소
#     # parking = 이거 어떻게 지정해야되지?

# user:like = 1:N     
# class Like(models.Model):
#     # pK를 어떻게 지정하지? 얘 고유의 id값이 의미가 있어?
#     # user의 id를 fk로
#     user_id = models.ForeignKey(
#         User, 
#         on_delete=models.CASCADE, 
#         #related_name='like_author'
#     )
#     # fesstival의 id를 fk로
#     festival_id = models.ForeignKey(
#         Festival, 
#         on_delete=models.CASCADE, 
#         related_name='like_festsival'
#     )

class Post(models.Model):
    # user의 id를 fk로
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='post_user'
    )
    # profile = models.ForeignKey(
    #     Profile, 
    #     on_delete=models.CASCADE, 
    #     related_name='post_profile'
    # )
     # 공연과 관련없는 게시글일수도 있잖아 --> 모델을 따로 만들어줘야하나?
    # fesstival의 id를 fk로
    festival= models.ForeignKey(
        Festival, 
        on_delete=models.CASCADE, 
        related_name='post_festsival',
        null=True,
        db_column="festival_id"
    ) #null= true 로 페스티벌 정보 없이도 만들수있게
    title = models.TextField(blank=True)
    body = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)
    hits = models.IntegerField(blank=True)
    category = models.TextField(blank=True)
    #카테고리의 내역"후기", "친구 구하기", "티켓 양도", "정보 공유"

    def __str__(self):
        return self.title    
    

class Comment(models.Model):
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='comment_user',
    )
    # profile = models.ForeignKey(
    #     Profile, 
    #     on_delete=models.CASCADE, 
    #     related_name='comment_profile'
    # )
    post = models.ForeignKey(
        Post, 
        null=True, 
        on_delete=models.CASCADE,
        related_name='comment_post',
        db_column="post_id"
    )
    
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment

class Option(models.Model):
    # fesstival의 id를 fk로
    festival= models.ForeignKey(
        Festival, 
        on_delete=models.CASCADE, 
        related_name='option_festsival'
    )
    user= models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='option_user'
    )
    option1 = models.IntegerField(blank=True,default=0)
    option2 = models.IntegerField(blank=True,default=0)
    option3 = models.IntegerField(blank=True,default=0)
    option4 = models.IntegerField(blank=True,default=0)
    option5 = models.IntegerField(blank=True,default=0)
    option6 = models.IntegerField(blank=True,default=0)
       # user_id를 가져올 필요가 있어? >> 유저가 한 페스티벌에 여러번 특징작성 방지

class OptionCount(models.Model):
    # fesstival의 id를 fk로
    festival= models.OneToOneField(Festival, on_delete=models.CASCADE,primary_key=True,related_name='option_count')
    check_num=models.IntegerField(blank=True,default=0)
    option1 = models.IntegerField(blank=True,default=0)
    option2 = models.IntegerField(blank=True,default=0)
    option3 = models.IntegerField(blank=True,default=0)
    option4 = models.IntegerField(blank=True,default=0)
    option5 = models.IntegerField(blank=True,default=0)
    option6 = models.IntegerField(blank=True,default=0)
    
    @receiver(post_save, sender=Festival)
    def create_festival_optioncount(sender, instance, created, **kwargs):
        if created:
              OptionCount.objects.create(festival=instance)
              

class FestivalImage(models.Model):
    festival_id = models.ForeignKey(Festival, related_name="festival_images", on_delete=models.CASCADE, db_column="festival_id")
    image_url = models.CharField(blank=True, max_length=200)
    
    class Meta:
        db_table = 'festival_image'
        
    
class PostImage(models.Model):
    post_id = models.ForeignKey(Post, related_name="post_images", on_delete=models.CASCADE, db_column="post_id")
    image_url = models.CharField(blank=True, max_length=200)
    
    class Meta:
        db_table = 'post_image'