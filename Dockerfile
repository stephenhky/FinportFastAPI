FROM python:3.12-slim
LABEL authors="irqmlnlp"

WORKDIR /var/task

COPY app/ ./app
COPY requirements.txt .

# install python
RUN apt-get update && \
  apt-get install -y \
  g++ \
  libc6 \
  make \
  cmake \
  unzip \
  libcurl4-openssl-dev
RUN pip install -U pip
RUN pip install -r requirements.txt
RUN pip install awslambdaric

ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
CMD [ "app.finport_fastapi.handler" ]
