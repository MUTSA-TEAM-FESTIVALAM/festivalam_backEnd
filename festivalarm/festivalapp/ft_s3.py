import boto3
import my_secrets
from botocore.exceptions import ClientError
import logging

def upload_file(file_path,file_name):

    # 파일 가져올 경로 
    file_path='파일 경로'
    # 생성한 bucket 이름 
    bucket = my_secrets.AWS_STORAGE_BUCKET_NAME

    # s3 파일 객체 이름
    object_name = file_name

    # aws region 
    location = 'ap-northeast-2'
   
    #자격 증명 
    s3_client = boto3.client(
    's3',
    aws_access_key_id=my_secrets.AWS_SECRET_ACCESS_KEY,
    aws_secret_access_key=my_secrets.AWS_SECRET_ACCESS_KEY
    )

     # Upload the file
    try:
        s3_client.upload_file(file_path, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return None
    image_url = f'https://{bucket}.s3.{location}.amazonaws.com/festival_img/{object_name}'
    return image_url