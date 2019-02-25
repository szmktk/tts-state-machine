FROM python:3-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV AWS_REGION eu-west-1
ENV ACTIVITY_ARN arn:aws:states:eu-west-1:************:activity:ProcessUsersSubscriptionActivity

CMD [ "python", "./activity_queue_poller.py" ]
