FROM python:3.8

COPY ./config /workdir/config
COPY ./migrations /workdir/migrations
COPY *.py /workdir/
COPY app.db /workdir/app.db
COPY ./requirements.txt /workdir/requirements.txt

WORKDIR /workdir

RUN pip install -r requirements.txt
EXPOSE 5000

ENTRYPOINT ["python", "app.py"]