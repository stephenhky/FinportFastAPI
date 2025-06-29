FROM python:3.12-slim
LABEL authors="irqmlnlp"

ADD . /app

# set the Docker working directory
WORKDIR /app

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
# RUN pip install awslambdaric boto3

# Launch the Uvicorn web server and run the application
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
# ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
CMD [ "app.finport_fastapi.handler" ]
