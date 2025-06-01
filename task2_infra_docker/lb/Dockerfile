# lb/Dockerfile

# Берём «чистый» Alpine образ Nginx
FROM nginx:stable-alpine

# Удаляем стандартный конфиг(и) из /etc/nginx/conf.d, чтобы не было «старых» сайтов
RUN rm -f /etc/nginx/conf.d/default.conf
RUN rm -rf /etc/nginx/conf.d/*.conf

# Копируем наш файл и заменяем основной конфиг
COPY nginx.conf /etc/nginx/nginx.conf
