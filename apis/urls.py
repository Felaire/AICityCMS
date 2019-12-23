from django.urls import path

from . import views

urlpatterns = [
    path('get_route', views.get_route, name='get_route'),
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('poi', views.poi_index, name='poi_index'),
    path('poi_search', views.poi_search, name='poi_search'),
    path('poi_version', views.poi_version, name='poi_verion'),
    path('activity', views.activity_index, name='activity_index'),
    path('beacon', views.beacon_index, name='beacon_index'),
    path('beacon_version', views.beacon_version, name='beacon_version'),
    path('beacon_search', views.beacon_search, name='beacon_verion'),
    path('activate', views.activate, name='activate'),
    path('record_coordinate', views.record_coordinate, name='record_coordinate'),
    path('heatmap', views.heatmap, name='heatmap'),
    path('poi_map', views.poi_map, name='poi_map'),
    path('location_track', views.location_track, name='location_track'),
    path('building', views.building_index, name='building_index'),
    path('building_version', views.building_version, name='building_version'),
    path('user_current', views.user_current, name='user_current'),
]