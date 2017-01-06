from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

import schedule
import time

from trax.trax import tasks


class Command(BaseCommand):
    help = 'Run the cron-like task to do recurring tasks'

    def handle(self, *args, **options):
        def job():
            print("I'm working...")

        schedule.every(1).hours.do(tasks.kill_obsolete_timers)

        self.stdout.write(self.style.SUCCESS('Starting job runner...'))
        while True:
            schedule.run_pending()
            time.sleep(1)
