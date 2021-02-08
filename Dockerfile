FROM ubuntu:18.04
MAINTAINER  Prabu "mprabu@gocontec.com"
ENV TZ=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update -y
RUN apt-get install libzbar0 -y
RUN apt-get install -y python3-pip python3-dev build-essential
RUN apt update && apt install -y libsm6 libxext6
RUN apt-get -y install tesseract-ocr
RUN apt-get -y install python3-tk
RUN apt-get -y install libmysqlclient-dev
RUN apt-get -y install gcc
RUN apt-get -y install python3-opencv
COPY . /app
WORKDIR /app
RUN pip3 install js2py
RUN pip3 install selenium
RUN pip3 install pillow
RUN pip3 install requests
RUN pip3 install Flask-Session
RUN pip3 install pytesseract
RUN pip3 install -r requirements.txt
RUN pip3 install --user Werkzeug==0.16
RUN pip3 install pyzbar
RUN pip3 install flask flask-jsonpify flask-sqlalchemy flask-restful
RUN pip3 freeze
RUN pip3 install mysqlclient
ENTRYPOINT ["python3"]
CMD ["app.py"]