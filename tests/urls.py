from django.conf import settings
from django.urls import include, path
from django.views.static import serve

urlpatterns = [
    path("media/<path:path>", serve, {"document_root": settings.MEDIA_ROOT,}),
    path(
        "",
        include(
            "webhooks.urls", namespace="webhooks"
        ),
    ),
]
