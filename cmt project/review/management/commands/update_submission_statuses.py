from django.core.management.base import BaseCommand
from review.models import Review

class Command(BaseCommand):
    help = 'Update all submission statuses based on their reviews'

    def handle(self, *args, **options):
        self.stdout.write('Updating submission statuses...')
        
        # Update all submission statuses
        Review.update_all_submission_statuses()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully updated all submission statuses!')
        ) 