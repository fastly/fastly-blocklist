FROM python:3-alpine


WORKDIR /fastly-blocklist

RUN pip install pipenv

COPY . .

RUN pipenv install --system --deploy --ignore-pipfile

ENTRYPOINT ["python", "./fastly-blocklist.py"]
