FROM python:3.12-slim
LABEL authors="irqmlnlp"

COPY ./app ${LAMBDA_TASK_ROOT}
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# set the Docker working directory
#WORKDIR /app

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
RUN #pip install awslambdaric boto3

#ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
CMD [ "app.finport_fastapi.handler" ]
