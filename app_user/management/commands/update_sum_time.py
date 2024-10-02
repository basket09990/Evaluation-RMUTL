from django.core.management.base import BaseCommand
from app_user.models import Profile
from datetime import datetime, date

class Command(BaseCommand):
    help = 'Update sum_time_goverment for all profiles'

    def handle(self, *args, **kwargs):
        profiles = Profile.objects.all()
        today = date.today()

        for profile in profiles:
            if profile.start_goverment and isinstance(profile.start_goverment, date):
                days_passed = (today - profile.start_goverment).days
            else:
                days_passed = 0  # หรือกำหนดให้เป็น None ตามต้องการ

            profile.sum_time_goverment = days_passed
            profile.save()

        self.stdout.write(self.style.SUCCESS('Successfully updated sum_time_goverment for all profiles'))