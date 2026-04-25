from django.core.management.base import BaseCommand
from apps.cards.services.sync_service import CardSyncService


class Command(BaseCommand):
    help = 'Sync reference data from external APIs'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Syncing reference data...'))
        try:
            service = CardSyncService()
            service.sync_reference_data()
            self.stdout.write(self.style.SUCCESS('Reference data synced successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error syncing reference data: {str(e)}'))
