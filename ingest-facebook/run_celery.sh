#!/bin/sh

# wait for PSQL server to start
while ! curl --max-time 30 http://db:5432/ 2>&1 | grep '52'
do
    echo "Waiting for database..."
    sleep 1
done

cd django_facebook

# run Celery worker for our project myproject with Celery configuration stored in Celeryconf
celery -A ingestion_facebook.tasks worker -f /var/log/celery.log





