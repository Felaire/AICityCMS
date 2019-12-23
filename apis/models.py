from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Node(models.Model):
    id = models.CharField(primary_key=True, max_length=20)
    lat = models.CharField(max_length=100)
    lon = models.CharField(max_length=100)
    level = models.CharField(max_length=100, default='')
    weight = models.CharField(max_length=100, default='')

class Edge(models.Model):
    id = models.CharField(primary_key=True, max_length=20)
    from_node = models.CharField(max_length=20, default='')
    to_node = models.CharField(max_length=20, default='')

class Route(models.Model):
    from_node = models.CharField(max_length=20, default='')
    to_node = models.CharField(max_length=20, default='')
    nodes = models.CharField(max_length=5000, default='')
    edges = models.CharField(max_length=5000, default='')

class Token(models.Model):
    token = models.CharField(primary_key=True, max_length=100)
    generated_time = models.DateTimeField()
    expired_time = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)

class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.IntegerField()
    active_code = models.CharField(max_length=10, default='')
    current_latitude = models.CharField(max_length=100, default='')
    current_longitude = models.CharField(max_length=100, default='')

class UserDevice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=100, default='', unique=True)
    device_platform = models.CharField(max_length=20, default='')

class DeviceCoordinate(models.Model):
    device = models.ForeignKey(UserDevice, on_delete=models.CASCADE)
    latitude = models.CharField(max_length=100)
    longitude = models.CharField(max_length=100)
    level_code = models.CharField(max_length=10, default='')
    captured_time = models.DateTimeField()

class Tile(models.Model):
    tile_code = models.CharField(max_length=100, unique=True)

class TilePoiVersion(models.Model):
    tile = models.OneToOneField(Tile, on_delete=models.CASCADE)
    version = models.DateTimeField()

class TileBeaconVersion(models.Model):
    tile = models.OneToOneField(Tile, on_delete=models.CASCADE)
    version = models.DateTimeField()

class Poi(models.Model):
    name = models.CharField(max_length=500)
    title = models.CharField(max_length=500, default='')
    latitude = models.FloatField()
    longitude = models.FloatField()
    level_code = models.CharField(max_length=50)
    map_scale = models.IntegerField()
    staff = models.CharField(max_length=5, default='')
    tile = models.ForeignKey(Tile, default=1, on_delete=models.CASCADE)
    interest_type = models.IntegerField()
    building_name = models.CharField(max_length=100)
    map_scale = models.IntegerField()
    parking_field = models.BooleanField()
    visitor = models.BooleanField(default=False)
    descriptions_title = models.CharField(max_length=1000, default='')
    descriptions_text = models.CharField(max_length=2000, default='')
    website = models.CharField(max_length=200, default='')
    opening_text = models.CharField(max_length=200, default='')
    tel = models.CharField(max_length=50, default='')
    address = models.CharField(max_length=200, default='')
    poi_type = models.CharField(max_length=50, default='')

class PoiImage(models.Model):
    poi = models.ForeignKey(Poi, on_delete=models.CASCADE)
    url = models.CharField(max_length=2000)

class PoiOpeningDetail(models.Model):
    poi = models.ForeignKey(Poi, on_delete=models.CASCADE)
    index = models.CharField(max_length=200)
    days = models.CharField(max_length=200)
    hours = models.CharField(max_length=200)

class Activity(models.Model):
    name = models.CharField(max_length=200)
    index = models.IntegerField()
    image_url = models.CharField(max_length=200)
    venue = models.CharField(max_length=200)
    building = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
    level_code = models.CharField(max_length=50)
    website = models.CharField(max_length=200)

class Beacon(models.Model):
    plate_code = models.CharField(max_length=20)
    uuid = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=50)
    level_code = models.CharField(max_length=20)
    room_code = models.CharField(max_length=20)
    beacon_type = models.IntegerField()
    latitude = models.DecimalField(max_digits=50, decimal_places=30)
    longitude = models.DecimalField(max_digits=50, decimal_places=30)
    name = models.CharField(max_length=200)
    speakout = models.CharField(max_length=200)
    m_power = models.IntegerField()
    searchable = models.IntegerField()
    tile = models.ForeignKey(Tile, default=1, on_delete=models.CASCADE)
    building_id = models.CharField(max_length=50)
    building_name = models.CharField(max_length=100)
    room_name = models.CharField(max_length=100)
    indoor = models.IntegerField()

class Building(models.Model):
    name = models.CharField(max_length=40)
    building_id = models.CharField(max_length=20)
    unit = models.CharField(max_length=20)
    tile = models.ForeignKey(Tile, default=1, on_delete=models.CASCADE)

class BuildingLevel(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    level_code = models.CharField(max_length=10)
    abbreviation = models.CharField(max_length=10)

class BuildingFloorPlan(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    level_code = models.CharField(max_length=10)

class BuildingFloorPlanBoundary(models.Model):
    buildingfloorplan = models.ForeignKey(BuildingFloorPlan, on_delete=models.CASCADE, default=1)
    boundary_id = models.CharField(max_length=20)
    latitude = models.CharField(max_length=30)
    longitude = models.CharField(max_length=30)
    sequence = models.IntegerField()

class TileBuildingVersion(models.Model):
    tile = models.OneToOneField(Tile, on_delete=models.CASCADE)
    version = models.DateTimeField()