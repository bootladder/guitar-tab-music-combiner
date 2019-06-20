from python:2.7

RUN pip install opencv-python
RUN pip install flask

# run app
WORKDIR /opt/app/webapp
CMD ["python","-u","app.py"]
