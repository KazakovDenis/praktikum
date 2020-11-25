import datetime
import os
from urllib.parse import urljoin

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import requests


@receiver(post_save, sender='movies.Person', dispatch_uid='congratulatory_signal')
def congratulatory(sender, instance, created, **kwargs):
    if created and instance.birth_date == datetime.date.today():
        print(f"У {instance.full_name} сегодня день рождения!")


@receiver([post_save, post_delete], sender=None, dispatch_uid='run_etl_signal')
class ETLRunner:
    """ETL processes runner"""

    address = os.getenv('ETL_ADDRESS', 'http://127.0.0.1:8050')
    processes = 'filmwork', 'genre', 'person'

    def __init__(self, signal, sender, **named):
        """Start an etl process to update Elasticsearch index"""
        etl_name = sender._meta.model_name
        if etl_name in self.processes:
            self.run(etl_name)

    def run(self, process):
        """Send http request to start ETL process"""
        url = urljoin(self.address, process)
        requests.get(url)
