from django.core.management.base import BaseCommand
from django.core.management import call_command
from datetime import datetime

class Command(BaseCommand):
    help = 'Backup database to Dropbox'

    def handle(self, *args, **options):
        try:
            self.stdout.write('Creating database backup...')
            call_command('dbbackup')
            self.stdout.write(self.style.SUCCESS('Successfully created database backup'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Backup failed: {str(e)}'))