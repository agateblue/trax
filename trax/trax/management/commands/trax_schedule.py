import traceback
import schedule
import time

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from trax.trax import tasks


class Command(BaseCommand):
    help = 'Run the cron-like task to do recurring tasks'

    def handle(self, *args, **options):
        def job():
            print("I'm working...")

        schedule.every(1).hours.do(tasks.kill_obsolete_timers)
        schedule.every(10).seconds.do(tasks.send_reminders)

        self.stdout.write(self.style.SUCCESS('Starting job runner...'))
        while True:
            time.sleep(1)
            try:
                schedule.run_pending()
            except:
                traceback.print_exc()
