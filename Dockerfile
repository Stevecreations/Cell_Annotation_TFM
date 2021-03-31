FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8050
#CMD export DISPLAY =":0"

CMD ["python", "./app_V5.py"]

#-e DISPLAY=$DISPLAY \
#-v /tmp/.X11-unix:/tmp/.X11-unix:rw