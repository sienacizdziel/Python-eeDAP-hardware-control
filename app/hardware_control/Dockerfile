FROM python:3

ADD ./app.py ./proscan.py ./base_stage.py ./check_ports.py /

RUN pip install future==0.18.2
RUN pip install iso8601==1.0.2
RUN pip install pyserial==3.5
RUN pip install PyYAML==6.0
RUN pip install Flask

CMD [ "python", "./app.py" ]