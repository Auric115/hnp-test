FROM python:3.13

WORKDIR /app
COPY service/ /app/
RUN pip install flask

ENV FLAG=HNP{default_flag}
CMD ["python", "app.py"]
