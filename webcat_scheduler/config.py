# This configuration file is copied to all Flask services that require it.
# Modifications made to this file will be reflected in all services.

SQL_HOST = 'host.docker.internal'
SQL_PORT = 5432
SQL_DATABASE = 'webcat_db'
SQL_USER = 'postgres'
SQL_PASSWORD = 'postgres'
SQLALCHEMY_DATABASE_URI = f'postgresql://{SQL_USER}:{SQL_PASSWORD}@{SQL_HOST}:{SQL_PORT}/{SQL_DATABASE}'