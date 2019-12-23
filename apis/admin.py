from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Node)
admin.site.register(Edge)
admin.site.register(Route)
admin.site.register(Tile)
admin.site.register(Poi)
admin.site.register(PoiImage)
admin.site.register(PoiOpeningDetail)
admin.site.register(Activity)
admin.site.register(Beacon)
admin.site.register(TilePoiVersion)
admin.site.register(TileBeaconVersion)
admin.site.register(UserInfo)
admin.site.register(UserDevice)
admin.site.register(DeviceCoordinate)
