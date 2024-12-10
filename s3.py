import boto3
import pandas as pd
import io
import botocore
from dotenv import load_dotenv
import os

load_dotenv()

REGION = "ap-south-1"
ACCESS_KEY_ID = os.getenv('ACCESS_KEY_ID')
SECRET_ACCESS_KEY = os.getenv('SECRET_ACCESS_KEY')
BUCKET_NAME = "darksysbucket"
KEY = "TrendingProducts/trendingproducts_jnjaiph.csv"

s3c = boto3.client(
        's3', 
        region_name = REGION,
        aws_access_key_id = ACCESS_KEY_ID,
        aws_secret_access_key = SECRET_ACCESS_KEY
    )

def isKeyExist(key):
    try:
        s3c.head_object(Bucket = BUCKET_NAME, Key = key)
        return True
    except botocore.exceptions.ClientError as e:
        return False

def getDfFromS3(key, skip_rows, columns_names, range_value, special_case):
    obj = s3c.get_object(Bucket= BUCKET_NAME , Key = key)
    df = None
    if special_case:
        df = pd.read_csv(io.BytesIO(obj['Body'].read()), encoding='utf8',header=None, names=columns_names, usecols=range(range_value), skiprows=skip_rows)
    else:
        df = pd.read_csv(io.BytesIO(obj['Body'].read()), encoding='utf8')
    return df

def read_file_from_s3(file_key):
    obj = s3c.get_object(Bucket=BUCKET_NAME, Key=file_key)
    
    # Read the file content (assuming it's a text file)
    file_content = obj['Body'].read().decode('utf-8')
    
    return file_content

"""
https://medium.com/@victor.perez.berruezo/download-a-csv-file-from-s3-and-create-a-pandas-dataframe-in-python-ffdb08c2967c

https://towardsthecloud.com/aws-sdk-key-exists-s3-bucket-boto3

https://dev.to/idrisrampurawala/efficiently-streaming-a-large-aws-s3-file-via-s3-select-4on
"""