from django.db import migrations
from pgvector.django import VectorExtension


class Migration(migrations.Migration):
    dependencies = [
        ("documents", "0001_initial"),  # Adjust this to your previous migration
    ]

    operations = [VectorExtension()]
