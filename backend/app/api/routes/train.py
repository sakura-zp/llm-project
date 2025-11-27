"""列车票务API路由"""

from fastapi import APIRouter, Query
from ...models.schemas import TrainQueryRequest, TrainQueryResponse, TrainStation, ErrorResponse
from ...services.train_service import get_train_service

router = APIRouter(tags=["train"])

train_service = get_train_service()


@router.post(
    "/train/search-tickets",
    response_model=TrainQueryResponse,
    summary="查询列车余票",
    description="根据出发城市、到达城市和日期查询12306列车余票信息"
)
async def search_tickets(request: TrainQueryRequest):
    """
    查询列车余票信息
    
    Args:
        request: 查询请求，包含train_date、from_station、to_station
        
    Returns:
        列车票信息列表
        
    Example:
        ```json
        {
            "train_date": "2025-06-01",
            "from_station": "苏州",
            "to_station": "青岛"
        }
        ```
    """
    try:
        print(f"\n🔍 开始查询列车余票...")
        print(f"   日期: {request.train_date}")
        print(f"   从: {request.from_station}")
        print(f"   到: {request.to_station}")
        
        # 调用服务层的查询方法
        tickets = await train_service.search_tickets(
            train_date=request.train_date,
            from_station=request.from_station,
            to_station=request.to_station
        )
        
        print(f"✅ 查询成功，找到 {len(tickets)} 个列车班次")
        
        return TrainQueryResponse(
            success=True,
            message="查询成功",
            data=tickets
        )
        
    except Exception as e:
        print(f"❌ 查询失败: {str(e)}")
        return TrainQueryResponse(
            success=False,
            message=f"查询失败: {str(e)}",
            data=[]
        )


@router.get(
    "/train/stations",
    response_model=dict,
    summary="查询城市车站",
    description="根据城市名查询所有车站信息"
)
async def get_stations(city: str = Query(..., description="城市名称")):
    """
    查询指定城市的所有车站
    
    Args:
        city: 城市名称
        
    Returns:
        车站信息列表
        
    Example:
        ```
        /api/train/stations?city=苏州
        ```
    """
    try:
        print(f"\n🏛️  查询城市车站: {city}")
        
        stations = await train_service.get_stations_by_city(city)
        
        print(f"✅ 查询成功，找到 {len(stations)} 个车站")
        
        return {
            "success": True,
            "message": "查询成功",
            "city": city,
            "data": [station.model_dump() for station in stations]
        }
        
    except Exception as e:
        print(f"❌ 查询失败: {str(e)}")
        return {
            "success": False,
            "message": f"查询失败: {str(e)}",
            "city": city,
            "data": []
        }


@router.get(
    "/train/station-code",
    response_model=dict,
    summary="查询城市主车站",
    description="根据城市名查询城市对应的主车站代码"
)
async def get_station_code(city: str = Query(..., description="城市名称")):
    """
    查询指定城市的主车站代码
    
    Args:
        city: 城市名称
        
    Returns:
        车站信息
        
    Example:
        ```
        /api/train/station-code?city=北京
        ```
    """
    try:
        print(f"\n🏢 查询城市主车站: {city}")
        
        station = await train_service.get_station_code(city)
        
        if station:
            print(f"✅ 查询成功: {station.station_name}")
            return {
                "success": True,
                "message": "查询成功",
                "data": station.model_dump()
            }
        else:
            print(f"⚠️  未找到车站")
            return {
                "success": False,
                "message": f"未找到城市 {city} 的主车站",
                "data": None
            }
        
    except Exception as e:
        print(f"❌ 查询失败: {str(e)}")
        return {
            "success": False,
            "message": f"查询失败: {str(e)}",
            "data": None
        }


@router.get(
    "/train/station-by-name",
    response_model=dict,
    summary="按名称查询车站",
    description="根据车站名称查询车站代码"
)
async def get_station_by_name(station_name: str = Query(..., description="车站名称")):
    """
    按车站名查询车站代码
    
    Args:
        station_name: 车站名称
        
    Returns:
        车站信息
        
    Example:
        ```
        /api/train/station-by-name?station_name=苏州北
        ```
    """
    try:
        print(f"\n🔎 按名称查询车站: {station_name}")
        
        station = await train_service.get_station_by_name(station_name)
        
        if station:
            print(f"✅ 查询成功: {station.station_name}")
            return {
                "success": True,
                "message": "查询成功",
                "data": station.model_dump()
            }
        else:
            print(f"⚠️  未找到车站")
            return {
                "success": False,
                "message": f"未找到车站: {station_name}",
                "data": None
            }
        
    except Exception as e:
        print(f"❌ 查询失败: {str(e)}")
        return {
            "success": False,
            "message": f"查询失败: {str(e)}",
            "data": None
        }


@router.get(
    "/train/route-stations",
    response_model=dict,
    summary="查询列车途径站",
    description="根据列车号查询列车途径的所有车站信息"
)
async def get_train_route_stations(train_number: str = Query(..., description="列车号，如G222")):
    """
    查询列车途径站点信息
    
    Args:
        train_number: 列车号（如 G222、D101 等）
        
    Returns:
        列车路线信息
        
    Example:
        ```
        /api/train/route-stations?train_number=G222
        ```
    """
    try:
        print(f"\n📍 查询列车途径站点: {train_number}")
        
        route = await train_service.get_train_route_stations(train_number)
        
        if route:
            print(f"✅ 查询成功，列车 {train_number} 途径 {len(route.stations)} 个车站")
            return {
                "success": True,
                "message": "查询成功",
                "data": route.model_dump()
            }
        else:
            print(f"⚠️  未找到列车信息")
            return {
                "success": False,
                "message": f"未找到列车: {train_number}",
                "data": None
            }
        
    except Exception as e:
        print(f"❌ 查询失败: {str(e)}")
        return {
            "success": False,
            "message": f"查询失败: {str(e)}",
            "data": None
        }


@router.get(
    "/train/health",
    summary="列车服务健康检查",
    description="检查列车服务是否可用"
)
async def health_check():
    """列车服务健康检查"""
    return {
        "status": "healthy",
        "service": "12306列车票务服务",
        "message": "列车查询服务正常运行中"
    }
