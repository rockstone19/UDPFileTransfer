#Author: Peter Gutstein
FROM python:latest

ADD ingress/ingress.py /ingress/

WORKDIR /ingress/

EXPOSE 20001/udp

ENTRYPOINT ["python3", "-u", "ingress.py"]
