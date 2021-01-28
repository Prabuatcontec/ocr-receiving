FROM ubuntu:18.04
MAINTAINER Prabu "mprabu@gocontec.com"
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
RUN apt update && apt install -y libsm6 libxext6
RUN apt-get -y install tesseract-ocr
COPY . /app
WORKDIR /app
RUN pip install pillow
RUN pip install pytesseract
RUN pip install opencv-contrib-python
RUN pip install -r requirements.txt
RUN pip install --user Werkzeug==0.16
ENTRYPOINT ["python"]
CMD ["ocr.py"]