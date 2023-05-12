from django.contrib             import admin
from django.urls                import path,include
from django.conf.urls           import handler404, handler500
from django.conf                import settings as st
from django.conf.urls.static    import static 

import django

def custom_page_not_found(request):
    return django.views.defaults.page_not_found(request, None)

def custom_server_error(request):
    return django.views.defaults.server_error(request)

urlpatterns = [
    path("admin/"   , admin.site.urls),
    path(""         , include("deaf_undead.urls",namespace="deaf_undead")),
]


if  st.DEBUG:
    urlpatterns+= static(st.STATIC_URL,document_root=st.STATIC_ROOT)
    urlpatterns+= static(st.MEDIA_URL,document_root=st.MEDIA_ROOT)
