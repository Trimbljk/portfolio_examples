FROM nginx:1.23
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx/app.conf /etc/nginx/conf.d/
COPY ./app/assets /usr/share/nginx/html/restricteduse/assets
COPY ./app/assets /usr/share/nginx/html/dev/restricteduse/assets
