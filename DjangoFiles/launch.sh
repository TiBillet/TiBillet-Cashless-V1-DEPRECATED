cd /DjangoFiles
gunicorn Cashless.wsgi --log-level=debug --log-file /DjangoFiles/www/gunicorn.logs -w 5 -b 0.0.0.0:8000

