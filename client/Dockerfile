#Author: Peter Gutstein
FROM python:latest

ADD client/client.py /client/

WORKDIR /client/

VOLUME ./recievedFiles:/recievedFiles

ENTRYPOINT ["python3", "-u", "client.py"]
