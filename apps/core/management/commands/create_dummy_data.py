from django.core.management.base import BaseCommand

from apps.core.tests.example_data import create


class Command(BaseCommand):
    help = "Populates database for deployment environment."

    def handle(self, *args, **options):
        create()