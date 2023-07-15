from config.awsConfig import session
from dotenv import load_dotenv

load_dotenv()

class ObjectS3:
    def __init__(self):
        self.session_s3= session.client('s3')

    def upload_file(self, **config):
        try:

            bucket_name = config["bucket_name"]
            file_name = config["file_name"]
            content= config["file_content"]
            meta_data= config["meta_data"]

            response = self.session_s3.put_object(
                Body=content,
                Bucket=bucket_name,
                Key=file_name,
                Metadata=meta_data
            )
        except Exception as e:
            print(e)
            response = None
        finally:
            return response
    
    def get_object(self, **config):
        try:
            bucket_name = config["bucket_name"]
            file_name = config["file_name"]

            response = self.session_s3.get_object(
                Bucket=bucket_name,
                Key=file_name
            )

            return response['Body'].read(), response['Metadata']
        except Exception as e:
            print(e)
            return None, None

