import mimetypes
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.urls import include, path, re_path


admin.site.index_title = "Admin Dashboard"
admin.site.site_header = "Admin Dashboard"
admin.site.site_title  = "Cold Storage Management"


urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),            # Django admin route
    # Auth routes - login / register
    path('', include('authentication.urls')),
    path('', include('cold_rooms.urls')),
    path('', include('historical.urls')),
    path('api/', include('api.urls')),
    path('comms/', include('comms.urls')),
]
# urlpatterns = i18n_patterns(*urlpatterns, prefix_default_language=False)

# FIX: uvicorn throws 404 for static files
urlpatterns += staticfiles_urlpatterns()

# FIX: resource was blocked due to MIME type mismatch (X-Content-Type-Options: nosniff).
mimetypes.add_type("application/javascript", ".js", True)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]