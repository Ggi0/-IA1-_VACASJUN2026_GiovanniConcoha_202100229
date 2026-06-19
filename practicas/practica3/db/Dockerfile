FROM postgres:15

# Variables por defecto (pueden venir del .env también)
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres
ENV POSTGRES_DB=smart_invoice

# Copia el script SQL para inicializar la DB
COPY db.sql /docker-entrypoint-initdb.d/db.sql