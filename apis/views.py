from django.shortcuts import render
from django.http import HttpResponse
import json
from .models import *
from .utils import coordinate_to_meters
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
import math
import uuid
import datetime
import random
from django.core.mail import send_mail
from django.conf import settings
from django.template import loader
from kafka import KafkaProducer
from django.utils.safestring import SafeString
from itertools import groupby


# Create your views here.
def get_route(request):
    from_lat = request.POST.get('from_lat')
    from_lon = request.POST.get('from_lon')
    from_level = request.POST.get('from_level')
    to_lat = request.POST.get('to_lat')
    to_lon = request.POST.get('to_lon')
    to_level = request.POST.get('to_level')
    from_lat = float(from_lat)
    from_lon = float(from_lon)
    to_lat = float(to_lat)
    to_lon = float(to_lon)

    from_nodes = Node.objects.filter(level=from_level)
    to_nodes = Node.objects.filter(level=to_level)

    if len(from_nodes) == 0 or len(to_nodes) == 0:
        res = {
            'status': 'fail',
            'message': 'failed to find start or end node'

        }
        return HttpResponse(json.dumps(res))

    distance = float("inf")
    from_index = 0
    from_y, from_x = coordinate_to_meters(from_lat, from_lon)
    print("from coordinate: " + str(from_lat) + " " + str(from_lon))
    print("from meters: " + str(from_y) + " " + str(from_x))
    for index, node in enumerate(from_nodes):
        cur_y, cur_x = coordinate_to_meters(float(node.lat), float(node.lon))
        cur_distance = math.sqrt((cur_x - from_x)**2 + (cur_y - from_y)**2)
        print("node id:" + str(node.id))
        print("node coordinate: " + str(node.lat) + " " + str(node.lon))
        print("cur_meters: " + str(cur_y) + " " + str(cur_x))
        print("cur_distance: " + str(cur_distance))
        if cur_distance < distance:
            print("current min distance: " + str(cur_distance))
            distance = cur_distance
            from_index = index
    from_node = from_nodes[from_index]
    print("from_distance: "+ str(distance))

    print("\n\n\n")

    distance = float("inf")
    to_index = 0
    to_y, to_x = coordinate_to_meters(to_lat, to_lon)
    print("to coordinate: " + str(to_lat) + " " + str(to_lon))
    print("to meters: " + str(to_y) + " " + str(to_x))
    for index, node in enumerate(to_nodes):
        cur_y, cur_x = coordinate_to_meters(float(node.lat), float(node.lon))
        cur_distance = math.sqrt((cur_x - to_x)**2 + (cur_y - to_y)**2)
        print("node id:" + str(node.id))
        print("node coordinate: " + str(node.lat) + " " + str(node.lon))
        print("cur_meters: " + str(cur_y) + " " + str(cur_x))
        print("cur_distance: " + str(cur_distance))
        if cur_distance < distance:
            print("current min distance: " + str(cur_distance))
            distance = cur_distance
            to_index = index
    to_node = to_nodes[to_index]
    print("to_distance: "+ str(distance))

    print(str(from_node.id) + " " + str(to_node.id))
    routes = Route.objects.filter(from_node=from_node.id,to_node=to_node.id)
    
    #edges = route.edges.split(',')
    res_nodes = []
    #res_edges = []
    if len(routes) > 0:
        route = routes[0]
        nodes = route.nodes.split(',')
        for node_id in nodes:
            node_dict = {}
            node = Node.objects.get(pk=node_id)
            node_dict['id'] = node.id
            node_dict['lat'] = node.lat
            node_dict['lon'] = node.lon
            node_dict['level'] = node.level
            node_dict['weight'] = node.weight
            res_nodes.append(node_dict)
        """
        for edge_id in edges:
            edge_dict = {}
            edge = Edge.objects.get(pk=edge_id)
            edge_dict['id'] = edge.id
            edge_dict['from_node'] = edge.from_node
            edge_dict['to_node'] = edge.to_node
            res_edges.append(edge_dict)
        """
    res = {
        'status': 'success',
        'nodes': res_nodes,
        #'edges': res_edges
    }
    return HttpResponse(json.dumps(res))

def register(request):
    username = request.POST['username']
    password = request.POST['password']
    email = request.POST['email']
    user_type = request.POST['user_type']
    is_staff = False
    if (int(user_type) == 3):
        is_staff = True
    user = User.objects.create_user(username=username, email=email, is_staff=is_staff, is_active=False)
    user.set_password(password)
    user.is_active = True
    user.save()
    user_info = UserInfo(user_type=int(user_type))
    user_info.user = user
    

    active_code = ''
    for i in range(6):
        cur_code = random.randint(0,9)
        active_code += str(cur_code)
    user_info.active_code = active_code

    user_info.save()

    #send_mail('active code', 'active_code:'+active_code, settings.EMAIL_FROM, [email])

    res = {
        'status': 'success',
    }
    return HttpResponse(json.dumps(res))

def activate(request):
    username = request.POST['username']
    active_code = request.POST['active_code']
    user = User.objects.filter(username=username)[0]
    user_info = user.userinfo
    res = {}
    print(user_info.active_code)
    if active_code == user_info.active_code:
        user.is_active = True
        user.save()
        res = {
            'status': 'success'
        }
    else:
        res = {
            'status': 'failed',
            'reason': 'code error',
        }
    return HttpResponse(json.dumps(res))

def login(request):
    username = request.POST['username']
    password = request.POST['password']
    device_id = request.POST['device_id']
    device_platform = request.POST['device_platform']
    user = authenticate(username=username, password=password)
    res = {}
    if user is not None:
        if user.is_active:
            token_str = str(uuid.uuid1())
            current_time = datetime.datetime.now()
            expire_time = current_time + datetime.timedelta(days=300000)
            token = Token(token=token_str, generated_time=current_time, expired_time=expire_time, user=user)
            token.save()
            user_info = user.userinfo
            user_device, created = UserDevice.objects.get_or_create(user=user, device_id=device_id)
            if created:
                user_device.device_platform=device_platform
                user_device.save()
            res = {
                'status': 'success',
                'token': token_str,
                'user_type': user_info.user_type
            }
        else:
            res = {
                'status': 'failed',
                'reason': 'user not activated'
            }
    else:
        res = {
            'status': 'failed',
            'reason': 'username or password not match'
        }
    return HttpResponse(json.dumps(res))

def heatmap(request):
    user_infos = UserInfo.objects.all();
    template = loader.get_template('heatmap/heatmap.html')
    context = {
        'user_infos': user_infos,
    }
    return HttpResponse(template.render(context, request))

def location_track(request):
    device_id = request.GET['device_id']
    device = UserDevice.objects.filter(id=device_id)[0]
    device_userid = device.user_id
    device_coordinates = device.devicecoordinate_set.all()
    device_trackInfo = []
    device_time = {}
    device_alldate = []
    repeated_coordinates = []
    repeat_time = 0
    for device_coordinate in device_coordinates:
        # print(device_coordinate.latitude + ":" + device_coordinate.longitude)
        if device_coordinate.latitude == "nan" or device_coordinate.longitude == "nan":
            continue;    
        device_coordinate.latitude = float(device_coordinate.latitude) + 0
        device_coordinate.longitude = float(device_coordinate.longitude) + 0
        device_captured_time = str(device_coordinate.captured_time)[0:19]
        device_date = str(device_coordinate.captured_time)[0:10]
        if device_date not in device_alldate:
            device_alldate.append(device_date)
            device_time[device_date] = [device_captured_time]
        else:
            if device_captured_time not in device_time[device_date]:
                device_time[device_date].append(device_captured_time)
        device_levelCode = device_coordinate.level_code
        device_trackInfo_List = {"longitude": device_coordinate.longitude, "latitude": device_coordinate.latitude, "level_code":device_levelCode}
        device_trackInfo.append(device_trackInfo_List)
    template = loader.get_template('location_track/location_track.html')
    # 去除连续重复数据
    device_trackInfo = [x[0] for x in groupby(device_trackInfo)]
    context = {
        'device_track': device_trackInfo,
        'device_track_json': SafeString(device_trackInfo),
        'user_id': str(device.user_id),
        'device_time': SafeString(device_time)
    }
    return HttpResponse(template.render(context, request))

def user_current(request):
    user_id = request.POST['userId']
    user_info = UserInfo.objects.filter(id=int(user_id))[0]
    results = {"longitude":user_info.current_longitude, "latitude":user_info.current_latitude}
    return HttpResponse(json.dumps(results,default=str))

def poi_map(request):
    pois = Poi.objects.all();
    beacons = Beacon.objects.all();
    template = loader.get_template('poi_map/poi_map.html')
    context = {
        'pois': pois,
        'beacons': beacons
    }
    return HttpResponse(template.render(context, request))

def record_coordinate(request):
    device_id = request.POST['device_id']
    latitude = request.POST['latitude']
    longitude = request.POST['longitude']
    level_code = request.POST['level_code']
    captured_time = request.POST['captured_time']
    authorization = request.META['HTTP_AUTHORIZATION']
    authorization = authorization.split(' ')
    res = {}
    if authorization[0] != 'Token':
        res = {
            'status': 'failed',
            'reason': 'header not correct'
        }
    else:
        token = authorization[1]
        stored_token = Token.objects.filter(token=token)[0]
        if stored_token is None:
            res = {
                'status': 'failed',
                'reason': 'token not valid'
            }
        else:
            user = stored_token.user
            user_info = user.userinfo
            user_info.current_latitude = latitude
            user_info.current_longitude = longitude
            user_info.save()
            user_device = UserDevice.objects.get(device_id=device_id)
            device_coordinate = DeviceCoordinate(device=user_device, latitude=latitude,
                                                 longitude=longitude, level_code=level_code,
                                                 captured_time=captured_time)
            device_coordinate.save()

            
            msg_dict = {
                "device_id": device_id,
                "longitude": longitude,
                "latitude": latitude,
                "level_code": level_code,
                "captured_time": captured_time
            }
            try:
                producer = KafkaProducer(bootstrap_servers='127.0.0.1:9092')
                msg = json.dumps(msg_dict).encode('utf-8')
                producer.send('device_coordinate', msg, partition=0)
                producer.close()
            except Exception as e:
                print(str(e))
            res = {
                'status': 'success'
            }
    return HttpResponse(json.dumps(res))

def poi_index(request):
    request_tile_codes = request.POST['tile_code']
    print(request_tile_codes)
    tile_codes = request_tile_codes.split(';')
    tiles = []
    missed_tiles = []
    for code in tile_codes:
        tile_res = Tile.objects.filter(tile_code=code)
        if len(tile_res) > 0:
            tile = tile_res[0]
            tiles.append(tile)
        else:
            missed_tiles.append(code)
    results = {}
    results['result_code'] = 200
    tile_result = []
    for tile in tiles:
        tile_item = {}
        tile_item['tile_code'] = tile.tile_code
        if hasattr(tile, 'tilepoiversion'):
            poi_version = tile.tilepoiversion
            tile_item['tile_version'] = poi_version.version.timestamp()
            poi_result = []
            pois = tile.poi_set.all()
            for poi in pois:
                item = {}
                item['id'] = str(poi.id)
                item['title'] = poi.title
                item['level_code'] = poi.level_code
                item['name'] = poi.name
                item['poi_type'] = poi.poi_type
                item['latitude'] = poi.latitude
                item['longitude'] = poi.longitude
                item['building_name'] = poi.building_name
                item['map_scale'] = poi.map_scale
                item['staff'] = poi.staff
                item['tile_code'] = poi.tile.tile_code
                item['interest_type'] = poi.interest_type
                item['parking_field'] = (poi.parking_field == 1)
                item['visitor'] = poi.visitor
                item['address'] = poi.address
                item['tel'] = poi.tel
                image_records = poi.poiimage_set.all()
                images = []
                for image_record in image_records:
                    images.append(image_record.url)
                item['images'] = images
                opening = []
                detail_records = poi.poiopeningdetail_set.all()
                for detail_record in detail_records:
                    detail = {}
                    detail['index'] = detail_record.index
                    detail['days'] = detail_record.days
                    detail['hours'] = detail_record.hours
                    opening.append(detail)
                item['openning'] = opening
                description = {}
                description['title'] = poi.descriptions_title
                description['text'] = poi.descriptions_text
                item['introduction'] = description
                item['website'] = poi.website
                poi_result.append(item)
            tile_item['pois'] = poi_result
        else:
            tile_item['tile_version'] = 0
            tile_item['pois'] = []
        tile_result.append(tile_item)
    for tile_code in missed_tiles:
        tile_item = {
            'tile_code': tile_code,
            'tile_version': 0,
            'pois': []
        }
        tile_result.append(tile_item)
    results['tiles'] = tile_result
    return HttpResponse(json.dumps(results,default=str))

def poi_search(request):
    poi_result = []
    pois = Poi.objects.all()
    if 'name' in request.POST:
        name = request.POST['name']
        pois = pois.filter(name__contains=name)
    if 'type' in request.POST:
        poi_type = request.POST['type']
        pois = pois.filter(poi_type=poi_type)
    if 'id' in request.POST:
        pid = request.POST['id']
        pois = pois.filter(id=pid)
    results = {}
    results['result_code'] = 200
    for poi in pois:
        item = {}
        item['id'] = str(poi.id)
        item['title'] = poi.title
        item['level_code'] = poi.level_code
        item['name'] = poi.name
        item['poi_type'] = poi.poi_type
        item['latitude'] = poi.latitude
        item['longitude'] = poi.longitude
        item['building_name'] = poi.building_name
        item['map_scale'] = poi.map_scale
        item['staff'] = poi.staff
        item['tile_code'] = poi.tile_id
        item['interest_type'] = poi.interest_type
        item['parking_field'] = (poi.parking_field == 1)
        item['visitor'] = poi.visitor
        item['address'] = poi.address
        item['tel'] = poi.tel
        image_records = poi.poiimage_set.all()
        images = []
        for image_record in image_records:
            images.append(image_record.url)
        item['images'] = images
        opening = []
        detail_records = poi.poiopeningdetail_set.all()
        for detail_record in detail_records:
            detail = {}
            detail['index'] = detail_record.index
            detail['days'] = detail_record.days
            detail['hours'] = detail_record.hours
            opening.append(detail)
        item['openning'] = opening
        description = {}
        description['title'] = poi.descriptions_title
        description['text'] = poi.descriptions_text
        item['introduction'] = description
        item['website'] = poi.website
        poi_result.append(item)
    results['pois'] = poi_result
    return HttpResponse(json.dumps(results,default=str))

def beacon_search(request):
    beacon_result = []
    beacons = Beacon.objects.all()
    if 'uuid' in request.POST:
        uuid = request.POST['uuid']
        beacons = beacons.filter(uuid=uuid)
    if 'id' in request.POST:
        bid = request.POST['id']
        beacons = beacons.filter(id=bid)
    if 'type' in request.POST:
        beacon_type = request.POST['type']
        beacons = beacons.filter(beacon_type=beacon_type)
    results = {}
    results['result_code'] = 200
    for beacon in beacons:
        item = {}
        item['id'] = str(beacon.id)
        item['plate_code'] = beacon.plate_code
        item['uuid'] = beacon.uuid
        item['postal_code'] = beacon.postal_code
        item['level_code'] = beacon.level_code
        item['room_code'] = beacon.room_code
        item['beacon_type'] = beacon.beacon_type
        item['latitude'] = beacon.latitude
        item['longitude'] = beacon.longitude
        item['name'] = beacon.name
        item['speakout'] = beacon.speakout
        item['m_power'] = beacon.m_power
        item['searchable'] = beacon.searchable
        item['tile_code'] = beacon.tile_id
        item['building_id'] = beacon.building_id
        item['building_name'] = beacon.building_name
        item['room_name'] = beacon.room_name
        item['indoor'] = beacon.indoor
        beacon_result.append(item)
    results['beacons'] = beacon_result
    return HttpResponse(json.dumps(results,default=str))

def poi_version(request):
    request_tile_codes = request.POST['tile_code']
    tile_codes = request_tile_codes.split(';')
    tiles = []
    missed_tiles = []
    for code in tile_codes:
        tile_res = Tile.objects.filter(tile_code=code)
        if len(tile_res) > 0:
            tile = tile_res[0]
            tiles.append(tile)
        else:
            missed_tiles.append(code)
    results = {}
    results['result_code'] = 200
    tile_result = []
    for tile in tiles:
        tile_item = {}
        tile_item['tile_code'] = tile.tile_code
        if hasattr(tile, 'tilepoiversion'):
            poi_version = tile.tilepoiversion
            tile_item['tile_version'] = poi_version.version.timestamp()
        else:
            tile_item['tile_version'] = 0
        tile_result.append(tile_item)
    for tile_code in missed_tiles:
        tile_item = {
            'tile_code': tile_code,
            'tile_version': 0
        }
        tile_result.append(tile_item)
    results['tiles'] = tile_result
    return HttpResponse(json.dumps(results,default=str))

def activity_index(request):
    result = {}
    result['result_code'] = 200
    activities = []
    activity_records = Activity.objects.all()
    for activity_record in activity_records:
        activity = {}
        activity['name'] = activity_record.name
        activity['index'] = activity_record.index
        activity['image_url'] = activity_record.image_url
        activity['venue'] = activity_record.venue
        activity['building'] = activity_record.building
        activity['latitude'] = activity_record.latitude
        activity['longitude'] = activity_record.longitude
        activity['level_code'] = activity_record.level_code
        activity['website'] = activity_record.website
        activities.append(activity)
    result['activity'] = activities
    return HttpResponse(json.dumps(result))

def beacon_index(request):
    request_tile_codes = request.POST['tile_code']
    print(request_tile_codes)
    tile_codes = request_tile_codes.split(';')
    tiles = []
    missed_tiles = []
    for code in tile_codes:
        tile_res = Tile.objects.filter(tile_code=code)
        if len(tile_res) > 0:
            tile = tile_res[0]
            tiles.append(tile)
        else:
            missed_tiles.append(code)
    results = {}
    results['result_code'] = 200
    tile_result = []
    for tile in tiles:
        tile_item = {}
        tile_item['tile_code'] = tile.tile_code
        if hasattr(tile, 'tilebeaconversion'):
            beacon_version = tile.tilebeaconversion
            tile_item['tile_version'] = beacon_version.version.timestamp()
            beacon_result = []
            beacons = tile.beacon_set.all()
            for beacon in beacons:
                item = {}
                item['id'] = str(beacon.id)
                item['plate_code'] = beacon.plate_code
                item['uuid'] = beacon.uuid
                item['postal_code'] = beacon.postal_code
                item['level_code'] = beacon.level_code
                item['room_code'] = beacon.room_code
                item['beacon_type'] = beacon.beacon_type
                item['latitude'] = beacon.latitude
                item['longitude'] = beacon.longitude
                item['name'] = beacon.name
                item['speakout'] = beacon.speakout
                item['m_power'] = beacon.m_power
                item['searchable'] = beacon.searchable
                item['tile_code'] = beacon.tile.tile_code
                item['building_id'] = beacon.building_id
                item['building_name'] = beacon.building_name
                item['room_name'] = beacon.room_name
                item['indoor'] = beacon.indoor
                beacon_result.append(item)
            tile_item['beacons'] = beacon_result
        else:
            tile_item['tile_version'] = 0
            tile_item['beacons'] = []
        tile_result.append(tile_item)
    for tile_code in missed_tiles:
        tile_item = {
            'tile_code': tile_code,
            'tile_version': 0,
            'beacons': []
        }
        tile_result.append(tile_item)
    results['tiles'] = tile_result
    return HttpResponse(json.dumps(results,default=str))

def beacon_version(request):
    request_tile_codes = request.POST['tile_code']
    tile_codes = request_tile_codes.split(';')
    tiles = []
    missed_tiles = []
    for code in tile_codes:
        tile_res = Tile.objects.filter(tile_code=code)
        if len(tile_res) > 0:
            tile = tile_res[0]
            tiles.append(tile)
        else:
            missed_tiles.append(code)
    results = {}
    results['result_code'] = 200
    tile_result = []
    for tile in tiles:
        tile_item = {}
        tile_item['tile_code'] = tile.tile_code
        if hasattr(tile, 'tilebeaconversion'):
            beacon_version = tile.tilebeaconversion
            tile_item['tile_version'] = beacon_version.version.timestamp()
        else:
            tile_item['tile_version'] = 0
        tile_result.append(tile_item)
    for tile_code in missed_tiles:
        tile_item = {
            'tile_code': tile_code,
            'tile_version': 0
        }
        tile_result.append(tile_item)
    results['tiles'] = tile_result
    return HttpResponse(json.dumps(results, default=str))

def building_index(request):
    request_tile_codes = request.POST['tile_code']
    print(request_tile_codes)
    tile_codes = request_tile_codes.split(';')
    tiles = []
    missed_tiles = []
    for code in tile_codes:
        tile_res = Tile.objects.filter(tile_code=code)
        if len(tile_res) > 0:
            tile = tile_res[0]
            tiles.append(tile)
        else:
            missed_tiles.append(code)
    results = {}
    results['result_code'] = 200
    tile_result = []
    for tile in tiles:
        tile_item = {}
        tile_item['tile_code'] = tile.tile_code
        if hasattr(tile, 'tilebuildingversion'):
            building_version = tile.tilebuildingversion
            tile_item['tile_version'] = building_version.version.timestamp()
            building_result = []
            buildings = tile.building_set.all()
            for building in buildings:
                item = {}
                item['id'] = str(building.id)
                item['name'] = building.name
                item['buildingID'] = building.building_id
                item['unit'] = building.unit
                
                level_records = building.buildinglevel_set.all()
                levels = []
                for level_record in level_records:
                    level = {}
                    level['levelCode'] = level_record.level_code
                    level['abbreviation'] = level_record.abbreviation
                    levels.append(level)
                item['levels'] = levels

                floorplans = []
                floorplan_records = building.buildingfloorplan_set.all()
                for floorplan_record in floorplan_records:
                    floorplan = {}
                    floorplan['levelCode'] = floorplan_record.level_code

                    boundaries = []
                    boundary_records = floorplan_record.buildingfloorplanboundary_set.all()
                    for boundary_record in boundary_records:
                        boundary = {}
                        boundary['id'] = boundary_record.boundary_id
                        boundary['latitude'] = boundary_record.latitude
                        boundary['longitude'] = boundary_record.longitude
                        boundary['sequence'] = boundary_record.sequence
                        boundaries.append(boundary)
                    floorplan['boundary'] = boundaries
                    floorplans.append(floorplan)
                item['floorplans'] = floorplans
                building_result.append(item)
            tile_item['buildings'] = building_result
        else:
            tile_item['tile_version'] = 0
            tile_item['buildings'] = []
        tile_result.append(tile_item)
    for tile_code in missed_tiles:
        tile_item = {
            'tile_code': tile_code,
            'tile_version': 0,
            'buildings': []
        }
        tile_result.append(tile_item)
    results['tiles'] = tile_result
    return HttpResponse(json.dumps(results,default=str))

def building_version(request):
    request_tile_codes = request.POST['tile_code']
    tile_codes = request_tile_codes.split(';')
    tiles = []
    missed_tiles = []
    for code in tile_codes:
        tile_res = Tile.objects.filter(tile_code=code)
        if len(tile_res) > 0:
            tile = tile_res[0]
            tiles.append(tile)
        else:
            missed_tiles.append(code)
    results = {}
    results['result_code'] = 200
    tile_result = []
    for tile in tiles:
        tile_item = {}
        tile_item['tile_code'] = tile.tile_code
        if hasattr(tile, 'tilebuildingversion'):
            building_version = tile.tilebuildingversion
            tile_item['tile_version'] = building_version.version.timestamp()
        else:
            tile_item ['tile_version'] = 0
        tile_result.append(tile_item)
    for tile_code in missed_tiles:
        tile_item = {
            'tile_code': tile_code,
            'tile_version': 0
        }
        tile_result.append(tile_item)
    results['tiles'] = tile_result
    return HttpResponse(json.dumps(results, default=str))