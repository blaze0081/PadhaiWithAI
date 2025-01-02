from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        email = 'admin@padhaiwithai.com'
        new_password = 'padhaiwithai@2025'
        try:
            if not User.objects.filter(is_superuser=True).exists():
                self.stdout.write("No superusers found, creating one")
                User.objects.create_superuser(username='admin', email=email, password=new_password)
                self.stdout.write("=======================")
                self.stdout.write("A superuser has been created")
                self.stdout.write("Username: admin")
                self.stdout.write(f"Email: {email}")
                self.stdout.write(f"Password: {new_password}")

                self.stdout.write("=======================")
            else:
                self.stdout.write("A superuser exists in the database. Skipping.")
        except Exception as e:
            self.stderr.write(f"There was an error {e}")
