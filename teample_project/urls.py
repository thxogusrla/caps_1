"""teample_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import main.views#메인앱의 views함수를 임포트 해줍니다.

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('account.urls')),
    path('mail/', include('mail.urls')),
    path('team/', include('team.urls')),
    path('team_article/', include('team_article.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
