from django.urls import path
from django.contrib import admin
from django.contrib.auth import logout

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from ariadne.contrib.django.views import GraphQLView

from .schema import schema


urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('logout/', logout, {'next_page': '/'}, name='logout'),
    
    path('graphql/', csrf_exempt(GraphQLView.as_view(schema=schema)), name='graphql'),
    
]
