FROM nginx:1.29

RUN apt-get update && apt-get install -y apt-transport-https
RUN apt-get install -y vim

RUN rm /etc/nginx/conf.d/default.conf || true
COPY nginx.conf /etc/nginx/conf.d
