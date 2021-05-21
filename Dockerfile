FROM python:3

#Workdir on the image (unix System)
WORKDIR /usr/src/app

# Different python libraries to install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

#Copy everything in the folder to the work directory
COPY . .

# Comunication port between the dash application and the host machine
EXPOSE 8050


#Execute with python the application
CMD ["python", "./app_V6_lin.py"]

#Build instruction to launch from terminal

# docker build . -t "cell_annotation_v6"

# test intructions -- DO NOT UNCOMMENT
#CMD export DISPLAY =":0"
#-e DISPLAY=$DISPLAY \
#-v /tmp/.X11-unix:/tmp/.X11-unix:rw