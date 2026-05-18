from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),

    path('', include('users.urls')),

    path('', include('myapp.urls')),
)

urlpatterns += [
    path('i18n/', include('django.conf.urls.i18n')),
]

handler400 = 'myapp.views.handler400'
handler404 = 'myapp.views.handler404'
handler405 = 'myapp.views.handler405'
handler500 = 'myapp.views.handler500'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

