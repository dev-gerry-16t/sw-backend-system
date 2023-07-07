import boto3
from dotenv import load_dotenv
import os

load_dotenv()

aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region_name = os.getenv("REGION_AWS")


session = boto3.Session(
    aws_access_key_id = aws_access_key,
    aws_secret_access_key = aws_secret_key,
    region_name = aws_region_name
)


