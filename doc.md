# Route Search

## 入口

/get_route

## HTTP方法

GET

## 参数

from_lat: 起点latitude
from_lon: 起点longitude
from_level: 起点level
to_lat: 终点latitude
to_lon: 终点longitude
to_level: 终点level

##返回
{
    'status': 'success',
    'nodes': [
    ....
    ]
}

# POI List

## 入口

/poi

## HTTP方法

POST

## 参数

grid_code: 字符串，以分号分隔的grid_code列表

## 返回

{
    'result_code': 200,
    'grids':[
        {
            'grid_code': 'xxxx',
            'grid_version': 'xxxxx',
            'pois': [
                {
                    ....
                }
            ]
        },
        ...
    ]
}

# POI Search

## 入口

/poi_search

## HTTP方法

POST

## 参数

name: 字符串，搜索name字段的关键词
type: 搜索的类型

应当只传递上面两个参数中的一个，当同时传递两个参数时，则忽略type参数。

## 返回

{
    'result_code': 200,
    'pois': [
        {
            ....
        }
    ]
}


# POI Version

## 入口

/poi_version

## HTTP方法

POST

## 参数

grid_code: 字符串，以分号分隔的grid_code列表

## 返回

{
    'result_code': 200,
    'grids': [
        {
            'grid_code': 'xxxx',
            'grid_version': 'xxxxx'
        }
    ]
}

# Activity List

## 入口

/activity

## HTTP方法

POST

## 参数
无需要传递的参数

## 返回

{
    'result_code': 200,
    'activity':[
        {
            ...
        },
        ...
    ]
}
