FROM ubuntu:18.04
MAINTAINER Prabu "mprabu@gocontec.com"
ENV TZ=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
RUN apt update && apt install -y libsm6 libxext6
RUN apt-get -y install tesseract-ocr python-tk
COPY . /app
WORKDIR /app
RUN pip install pillow
RUN pip install requests
RUN pip install Flask-Session
RUN pip install pytesseract
RUN pip install opencv-contrib-python
RUN pip install -r requirements.txt
RUN pip install --user Werkzeug==0.16
ENTRYPOINT ["python"]
CMD ["app.py"]