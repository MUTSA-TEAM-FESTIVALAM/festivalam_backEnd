import boto3
import my_secrets
from botocore.exceptions import ClientError
import logging
import uuid
import mimetypes

def upload_festival_img(file_path): #인코딩 정보 바탕으로 스태틱폴더에 다운받은 후 s3에 업로드 후 삭제 하는 방향으로~~~~가보자
                                        # 지금 문제는 이대로 업로드 할 시 그 링크 접속하면 이미지가 보여지는게 아닌 다운로드가 된다. 이럼 의미가없다
                                        # 그러므로 보토3 업로드 기능 시 타입지정(context-type, meta-data) & 인코딩 한 값으로 로컬에 파일 저장, 업로드 후 그 로컬파일 삭제 
                                        # 이 기능 구현하자~~~ 별거없다
                                        
    # 파일 가져올 경로 
    file_path=file_path
    
    # 생성한 bucket 이름 
    bucket = my_secrets.AWS_STORAGE_BUCKET_NAME
    
    # s3 파일 객체 이름
    object_name = str(uuid.uuid4()) # 랜덤 생성 

    # aws region 
    location = 'ap-northeast-2'
    
    # s3 key
    file_mime_type = mimetypes.guess_type(file_path)[0].split("/")[1]
    key = 'festival_img/' + object_name + "."+file_mime_type# 키는 버킷내에서 저장할 위치 (디렉토리+파일명 지정)
    #자격 증명
    s3_client = boto3.client(
    's3',
    aws_access_key_id=my_secrets.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=my_secrets.AWS_SECRET_ACCESS_KEY
    )
    # Upload the file
    try:
        s3_client.upload_file(file_path, bucket, key,ExtraArgs={"ContentType" :mimetypes.guess_type(file_path)[0]})
    except ClientError as e:
        logging.error(e)
        return None
    image_url = f'https://{bucket}.s3.{location}.amazonaws.com/{key}'
    return image_url


def delete_festival_img(s3_url):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=my_secrets.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=my_secrets.AWS_SECRET_ACCESS_KEY
    )
    str = s3_url.split("/")
    key = str[len(str) -2]  + "/" +str[len(str) -1]
    return s3_client.delete_object(Bucket='festivalarm', Key=key)
