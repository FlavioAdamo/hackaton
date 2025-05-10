from .models import DriveFolder, DriveFile, CalendarEvent
from django.contrib import admin

admin.site.register(DriveFolder)
admin.site.register(DriveFile)
admin.site.register(CalendarEvent)
