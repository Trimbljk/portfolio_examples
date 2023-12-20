FROM nginx:1.23
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx/app.conf /etc/nginx/conf.d/
COPY ./app/assets /usr/share/nginx/html/ecosystem/assets
COPY ./app/assets /usr/share/nginx/html/dev/ecosystem/assets
COPY ./app/assets /usr/share/nginx/html/ecosystem/dashboard/assets
COPY ./app/assets /usr/share/nginx/html/dev/ecosystem/dashboard/assets
