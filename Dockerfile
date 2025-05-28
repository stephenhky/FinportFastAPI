FROM python:3.12-slim
LABEL authors="irqmlnlp"

ADD . /code

# set the Docker working directory
WORKDIR /code

# install python
RUN pip install -U pip
RUN pip install -r requirements.txt

# Launch the Uvicorn web server and run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
