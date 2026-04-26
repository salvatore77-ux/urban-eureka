from django.core.management.base import BaseCommand
from octofit_tracker.models import YourModel  # Replace with your actual model

class Command(BaseCommand):
    help = 'Populate the octofit_db database with test data.'

    def handle(self, *args, **kwargs):
        # Create test instances
        YourModel.objects.create(field1='value1', field2='value2')  # Adjust with real fields
        YourModel.objects.create(field1='value3', field2='value4')  # Adjust with real fields

        self.stdout.write(self.style.SUCCESS('Successfully populated the database.'))