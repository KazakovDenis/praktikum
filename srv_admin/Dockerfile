# cmd to build:
#     docker build -t movies_admin:1.0 .
#
# cmd to run:
#     docker run -d \
#     --restart=on-failure:3 \
#     -p 8000:8000 \
#     -v /var/run/postgresql:/run/postgresql \
#     --env POSTGRES_USER=$POSTGRES_USER \
#     --env POSTGRES_PASS=$POSTGRES_PASS \
#     --env POSTGRES_IP=$POSTGRES_IP \
#     --name movies_admin \
#     movies_admin:1.0 \
#     gunicorn config/wsgi:application -c configs/gunicorn_conf.py
FROM debian:10
EXPOSE 8000/tcp
RUN apt-get update && apt-get install -y python3 python3-pip python3-dev libpq-dev
WORKDIR /www
COPY . .
RUN pip3 install --no-cache-dir -r requirements/production.txt && apt-get clean
CMD ["python3", "-m", "manage", "runserver"]
