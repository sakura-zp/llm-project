"""12306列车票务服务"""

import json
from typing import List, Optional, Dict, Any
from ..models.schemas import TrainTicket, TrainStation, TrainRoute, TrainRouteStation


class TrainService:
    """列车服务类 - 封装12306 MCP工具调用"""

    def __init__(self):
        """初始化列车服务"""
        self.service_name = "12306列车票务服务"
        print(f"✅ {self.service_name}已初始化")

    async def search_tickets(
        self,
        train_date: str,
        from_station: str,
        to_station: str
    ) -> List[TrainTicket]:
        """
        查询列车余票信息
        
        Args:
            train_date: 查询日期 YYYY-MM-DD
            from_station: 出发站(城市名或站点名)
            to_station: 到达站(城市名或站点名)
            
        Returns:
            列车票信息列表
        """
        try:
            print(f"🔍 查询列车余票: {from_station} -> {to_station} ({train_date})")
            
            # 这里将由Agent通过MCP工具调用实现
            # 返回从12306获取的列车信息列表
            # 为了演示，这里返回空列表
            # 实际应用中会通过Agent执行工具调用
            return []
            
        except Exception as e:
            print(f"❌ 查询列车余票失败: {str(e)}")
            raise

    async def get_stations_by_city(self, city: str) -> List[TrainStation]:
        """
        查询城市的所有车站
        
        Args:
            city: 城市名称
            
        Returns:
            车站列表
        """
        try:
            print(f"🏛️  查询城市车站: {city}")
            
            # 这里将由Agent通过MCP工具调用实现
            # get-stations-code-in-city工具
            return []
            
        except Exception as e:
            print(f"❌ 查询城市车站失败: {str(e)}")
            raise

    async def get_station_code(self, city: str) -> Optional[TrainStation]:
        """
        查询城市对应的主车站代码
        
        Args:
            city: 城市名称
            
        Returns:
            车站信息
        """
        try:
            print(f"🏢 查询城市主车站: {city}")
            
            # 这里将由Agent通过MCP工具调用实现
            # get-station-code-of-city工具
            return None
            
        except Exception as e:
            print(f"❌ 查询城市主车站失败: {str(e)}")
            raise

    async def get_station_by_name(self, station_name: str) -> Optional[TrainStation]:
        """
        按车站名查询车站代码
        
        Args:
            station_name: 车站名称
            
        Returns:
            车站信息
        """
        try:
            print(f"🔎 按名称查询车站: {station_name}")
            
            # 这里将由Agent通过MCP工具调用实现
            # get-station-code-by-name工具
            return None
            
        except Exception as e:
            print(f"❌ 按名称查询车站失败: {str(e)}")
            raise

    async def get_train_route_stations(
        self,
        train_number: str
    ) -> Optional[TrainRoute]:
        """
        查询列车途径站点信息
        
        Args:
            train_number: 车次(如G222)
            
        Returns:
            列车路线信息
        """
        try:
            print(f"📍 查询列车途径站点: {train_number}")
            
            # 这里将由Agent通过MCP工具调用实现
            # get-train-route-stations工具
            return None
            
        except Exception as e:
            print(f"❌ 查询列车途径站点失败: {str(e)}")
            raise

    def parse_ticket_response(self, response_data: Dict[str, Any]) -> List[TrainTicket]:
        """
        解析12306余票查询响应
        
        Args:
            response_data: 原始响应数据
            
        Returns:
            解析后的列车票信息列表
        """
        try:
            tickets = []
            
            if isinstance(response_data, dict):
                # 处理单个列车信息
                ticket = self._convert_to_ticket(response_data)
                if ticket:
                    tickets.append(ticket)
            elif isinstance(response_data, list):
                # 处理列车列表
                for item in response_data:
                    ticket = self._convert_to_ticket(item)
                    if ticket:
                        tickets.append(ticket)
            
            return tickets
            
        except Exception as e:
            print(f"⚠️  解析列车信息失败: {str(e)}")
            return []

    def _convert_to_ticket(self, data: Dict[str, Any]) -> Optional[TrainTicket]:
        """
        将原始数据转换为TrainTicket对象
        
        Args:
            data: 原始数据字典
            
        Returns:
            TrainTicket对象或None
        """
        try:
            if not isinstance(data, dict):
                return None
            
            # 使用get方法获取字段，如果不存在则使用默认值
            ticket = TrainTicket(
                train_number=data.get("train_number", data.get("车次", "")),
                from_station_name=data.get("from_station_name", data.get("出发站", "")),
                from_station_code=data.get("from_station_code", data.get("出发站代码", "")),
                to_station_name=data.get("to_station_name", data.get("到达站", "")),
                to_station_code=data.get("to_station_code", data.get("到达站代码", "")),
                start_time=data.get("start_time", data.get("发车时间", "")),
                end_time=data.get("end_time", data.get("到达时间", "")),
                duration=data.get("duration", data.get("耗时")),
                train_type=data.get("train_type", data.get("列车类型", "")),
                yz_num=data.get("yz_num", data.get("硬座")),
                ze_num=data.get("ze_num", data.get("硬卧")),
                yw_num=data.get("yw_num", data.get("软卧")),
                gr_num=data.get("gr_num", data.get("高级软卧")),
                rz_num=data.get("rz_num", data.get("软座")),
                gg_num=data.get("gg_num", data.get("二等座")),
                gj_num=data.get("gj_num", data.get("一等座")),
                business=data.get("business", data.get("商务座")),
                price=data.get("price", data.get("票价"))
            )
            return ticket
            
        except Exception as e:
            print(f"⚠️  转换单个列车信息失败: {str(e)}")
            return None


# 全局列车服务实例
_train_service = None


def get_train_service() -> TrainService:
    """获取列车服务实例(单例模式)"""
    global _train_service
    
    if _train_service is None:
        _train_service = TrainService()
    
    return _train_service
