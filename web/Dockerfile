FROM nginx:latest

RUN echo 'Prepare the static resource\n'
ADD ./dist/ /data/ob-robot-web/

RUN echo 'Add nginx proxy server config\n'
COPY ./nginx.conf /etc/nginx/nginx.conf
