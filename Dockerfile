FROM nikolaik/python-nodejs:python3.7-nodejs16

WORKDIR /app
COPY angular-front ./angular-front
COPY backend ./backend
RUN apt-get update
RUN apt install -y libgl1-mesa-glx
RUN pip install -r backend/requirements.txt
RUN cd angular-front && npm install -g @angular/cli && npm install && ng build
ENTRYPOINT python backend/manage.py migrate && python backend/manage.py runserver 0.0.0.0:8080
