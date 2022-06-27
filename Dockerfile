FROM python:3.10.4-bullseye

WORKDIR /var/wordle

COPY ./requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

CMD ["python3", "load_wordle_tweets.py"]
