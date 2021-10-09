FROM nikolaik/python-nodejs:python3.7-nodejs16


RUN apt-get update
RUN apt install -y libgl1-mesa-glx

WORKDIR /app/backend
COPY backend/requirements.txt requirements.txt
RUN pip install -r requirements.txt
WORKDIR /app/angular-front
COPY angular-front/package.json package.json
RUN npm install -g @angular/cli && npm install 

WORKDIR /app
COPY angular-front angular-front
RUN cd angular-front && ng build
COPY backend backend
ENTRYPOINT python backend/manage.py migrate && python backend/manage.py runserver 0.0.0.0:8080
