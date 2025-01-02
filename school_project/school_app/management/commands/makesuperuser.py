from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        email = 'admin@padhaiwithai.com'
        new_password = get_random_string(6)
        try:
            # Delete existing superuser if exists
            User.objects.filter(is_superuser=True).delete()
            
            # Create new superuser
            User.objects.create_superuser(email=email, password=new_password)
            self.stdout.write("=======================")
            self.stdout.write("Superuser created/updated")
            self.stdout.write(f"Email: {email}")
            self.stdout.write(f"Password: {new_password}")
            self.stdout.write("=======================")
        except Exception as e:
            self.stderr.write(f"Error: {e}")
