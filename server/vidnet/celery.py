import os
from celery import Celery
# from celery.schedules import crontab
# from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vidnet.settings')

app = Celery('vidnet')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'every_10sec': {
        'task': 'hello2',
        'schedule': 3.0,
    },
}


# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')


# @app.task
# def test(arg):
#     print(arg)
