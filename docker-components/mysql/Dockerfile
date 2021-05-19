FROM mysql:5.7

ENV MYSQL_DATABASE docker
ENV MYSQL_USER docker
ENV MYSQL_ROOT_PASSWORD docker
ENV MYSQL_PASSWORD docker

RUN apt-get update && \
    apt-get install -y locales && \
    rm -rf /var/lib/apt/lists/* && \
    echo "ja_JP.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen ja_JP.UTF-8
ENV LC_ALL ja_JP.UTF-8

RUN { \
    echo '[mysqld]'; \
    echo 'character-set-server=utf8mb4'; \
    echo 'collation-server=utf8mb4_general_ci'; \
    echo 'collation-server=utf8mb4_general_ci'; \
    echo 'secure-file-priv=""'; \
    echo '[client]'; \
    echo 'default-character-set=utf8mb4'; \
} > /etc/mysql/conf.d/charset.cnf