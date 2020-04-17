ARG POSTGRES_TAG

FROM postgres:${POSTGRES_TAG}

COPY scripts/*.sh /usr/local/bin/

RUN chmod +x /usr/local/bin/*.sh 

COPY entrypoint/*.sql /docker-entrypoint-initdb.d/

RUN chmod a+r /docker-entrypoint-initdb.d/*
