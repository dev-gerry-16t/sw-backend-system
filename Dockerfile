FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

# ENV MONGO_HOST=mongodb+srv://gerardocto:zwVIPhzOFo1fcZJ1@swipdbcluster.cszyf.mongodb.net/
# ENV MONGO_DB=testswip
# ENV AWS_ACCESS_KEY_ID=AKIAWIBPGTYWFYJLSS6H
# ENV AWS_SECRET_ACCESS_KEY=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
# ENV AWS_ARN_SES_SWIP=arn:aws:ses:us-east-1:429595729452:identity/swip.mx
# ENV REGION_AWS=us-east-1
# ENV BUCKET_PERSONAL_DOCUMENT=swip.personaldocuments.test
# ENV BUCKET_PERSONAL_MORAL_DOCUMENT=swip.personalmoraldocuments.test
# ENV BUCKET_CAR_DOCUMENT=swip.cardocuments.test
# ENV BUCKET_CAR_MORAL_DOCUMENT=swip.carmoraldocuments.test
# ENV FRONT_END_ADMIN_URL=https://admin.swip.mx
# ENV FRONT_END_CLIENT_URL=https://beta.swip.mx
# ENV STRIPE_API_KEY=sk_test_51NdnkHGOflXpNNOPAGE7i0s3mR56sWoP2XXAW9RTm61JDMwhhFxnW6vi5o77rEMF8qp95io0PIXBEBGx6C7LWj6u007fX2VMu9
# ENV STRIPE_WEBHOOK_SECRET=whsec_e364afce18aa3450efccc88d7491e342ccac73750254d99b154827699ee8c4b1

CMD ["uvicorn", "app:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80","--forwarded-allow-ips", "*"]