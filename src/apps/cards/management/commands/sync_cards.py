from django.core.management.base import BaseCommand
from apps.cards.services.sync_service import CardSyncService


class Command(BaseCommand):
    help = 'Sync cards data from external APIs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--set_id',
            type=str,
            help='ID of the card set to sync (optional)'
        )

    def handle(self, *args, **options):
        set_id = options.get('set_id')
        
        if set_id:
            self.stdout.write(self.style.SUCCESS(f'Syncing cards data for set {set_id}...'))
        else:
            self.stdout.write(self.style.SUCCESS('Syncing all cards data...'))
            
        try:
            service = CardSyncService()
            created, updated, failed = service.sync_cards(set_id=set_id)
            self.stdout.write(self.style.SUCCESS(f'Cards data synced successfully! (Created: {created}, Updated: {updated}, Failed: {failed})'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error syncing cards data: {str(e)}'))
