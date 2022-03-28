FROM python:3.9

WORKDIR /slack_app

ADD . /slack_app

RUN pip install --upgrade pip
RUN pip install --trusted-host pipy.python.org --upgrade --force-reinstall --no-cache-dir -r requirements.txt

CMD ["python", "slackjokebot.py"]