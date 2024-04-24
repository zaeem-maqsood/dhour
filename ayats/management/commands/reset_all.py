# myapp/management/commands/run_multiple.py

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.conf import settings
import sys, os, glob


class Command(BaseCommand):
    help = "Runs multiple Django management commands to rest the database and reseed the data"

    def handle(self, *args, **kwargs):
        # Delete migration files
        base_dir = settings.BASE_DIR  # Project's base directory
        for app in os.listdir(base_dir):
            migrations_path = os.path.join(base_dir, app, "migrations")
            if os.path.isdir(migrations_path):
                migration_files = glob.glob(os.path.join(migrations_path, "*.py"))
                for migration_file in migration_files:
                    if "__init__.py" not in migration_file:
                        os.remove(migration_file)
                        self.stdout.write(f"Deleted: {migration_file}")

        # Delete the SQLite database file
        sqlite_db = os.path.join(base_dir, "db.sqlite3")
        if os.path.exists(sqlite_db):
            os.remove(sqlite_db)
            self.stdout.write(f"Deleted: {sqlite_db}")

        commands = ["makemigrations", "migrate", "bootstrap_data"]
        for command in commands:
            try:
                self.stdout.write(f"Running command: {command}")
                call_command(command)  # Execute the specified command
                self.stdout.write(
                    self.style.SUCCESS(f"Command {command} executed successfully")
                )
            except CommandError as e:
                self.stderr.write(self.style.ERROR(f"Command {command} failed: {e}"))
                sys.exit(1)  # Exit with an error status if a command fails
