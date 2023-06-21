"""stud URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

weburls = [
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    weburls += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
    weburls += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)

apiurls = [
    path('api/', include('accounts.urls')),
    path('api/auth/', include('knox.urls')),
    path('api/domains/', include('domains.urls')),
]

SchemaView = get_schema_view(
   openapi.Info(
      title = "Stud API",
      default_version = 'v1',
      description = "Stud API",
   ),
   patterns = apiurls,
   public = True,
   permission_classes = [permissions.AllowAny],
)

urlpatterns = weburls + apiurls + [
   re_path(r'^api/swagger/$',
    SchemaView.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

urlpatterns += [
    # path('admin/', admin.site.urls),
    path('api/', include('rest_framework.urls')),
    path('', include('uploader.urls')),
]
