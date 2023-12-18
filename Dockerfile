from python:3.7

RUN pip3 install opencv-python
RUN pip3 install flask

# run app
WORKDIR /opt/app/webapp
CMD ["python","-u","app.py"]
