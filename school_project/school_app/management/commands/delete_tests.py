from django.core.management.base import BaseCommand
from school_app.models import Test

class Command(BaseCommand):
    help = 'Deletes all Test objects from the database'

    def handle(self, *args, **kwargs):
        try:
            deleted_count, _ = Test.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted {deleted_count} Test objects')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error occurred: {e}')
            )
