from django.contrib import admin

from .models import Message, Room

# Register your models here.
admin.register(Room)
admin.register(Message)
