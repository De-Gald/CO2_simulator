FROM docker.io/gnuoctave/octave:6.4.0
USER root
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY . ./
CMD gunicorn -b 0.0.0.0:8080 python.web.app:server
