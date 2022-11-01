from django.core.management import BaseCommand
from bot import main


class Command(BaseCommand):
    def handle(self, *args, **options):
        main.run_bot()