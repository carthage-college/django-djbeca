# Apache Config
<pre>
WSGIDaemonProcess djbeca user=www-data group=www-data threads=1
WSGIScriptAlias /djbeca "/data2/django_projects/djbeca/wsgi.py" process-group=djbeca application-group=djbeca
<Location /djbeca>
    Require all granted
</Location>
</pre>
