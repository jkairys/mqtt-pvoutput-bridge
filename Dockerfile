FROM python:3.5
RUN  \
  pip3 install paho-mqtt requests

COPY *.py /opt/app/
COPY *.json /opt/app/

CMD ["python3", "/opt/app/main.py" , "settings.json"]
