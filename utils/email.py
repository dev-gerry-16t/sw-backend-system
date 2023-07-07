import os
import json
from config.awsConfig import session
from dotenv import load_dotenv

load_dotenv()

class Email:
    def __init__(self):
        self.session_ses= session.client('ses')
        self.aws_arn_ses_swip= os.getenv("AWS_ARN_SES_SWIP")


    def create_template_email(self, **config):
        template_name = config["template_name"]
        template_subject = config["template_subject"]
        template_text = config["template_text"]
        template_html = config["template_html"]

        response = self.session_ses.create_template(
            Template={
                'TemplateName': template_name,
                'SubjectPart': template_subject,
                'TextPart': template_text,
                'HtmlPart': template_html
            }
        )

        return response
    
    def send_email_template(self, **config):
        template_name = config["template_name"]
        email_to = config["email_to"]
        email_from = config["email_from"]
        template_data = config["template_data"]

        response = self.session_ses.send_templated_email(
            SourceArn=self.aws_arn_ses_swip,
            Source=email_from,
            Destination={
                'ToAddresses': [
                    email_to,
                ]
            },
            Template=template_name,
            TemplateData=json.dumps(template_data)
        )

        return response
