#Author: Peter Gutstein
FROM python:latest

ADD worker/worker.py /worker/
ADD worker/files /worker/

WORKDIR /worker/

ENTRYPOINT ["python3", "-u", "worker.py"]
