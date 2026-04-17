from django.contrib import admin

from .models import Country, ModelWithCustomTopic


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(ModelWithCustomTopic)
class ModelWithCustomTopicAdmin(admin.ModelAdmin):
    list_display = ("name",)