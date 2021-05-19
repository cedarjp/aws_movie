from django.core.management.base import BaseCommand
from app.utils import Predict

class Command(BaseCommand):
    help = ''

    def add_arguments(self, parser):
        parser.add_argument('s3_bucket_name')
        parser.add_argument('s3_key')

    def handle(self, *args, **options):
        s3_bucket_name = options.get('s3_bucket_name')
        s3_key = options.get('s3_key')
        predict = Predict(s3_bucket_name, s3_key)
        predict.run()
