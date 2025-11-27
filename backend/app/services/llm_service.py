"""LLM服务模块"""

import os
from hello_agents import HelloAgentsLLM
from ..config import get_settings

# 全局LLM实例
_llm_instance = None


def get_llm() -> HelloAgentsLLM:
    """
    获取LLM实例(单例模式)
    
    Returns:
        HelloAgentsLLM实例
    """
    global _llm_instance
    
    if _llm_instance is None:
        settings = get_settings()
        
        # 调试信息：打印config中读取的值
        print(f"[调试] 从settings读取的值:")
        print(f"  llm_api_key: {settings.llm_api_key[:10]}...")
        print(f"  llm_model: {settings.llm_model}")
        print(f"  llm_base_url: {settings.llm_base_url}")
        
        # 直接传参，不依赖环境变量，避免框架读取错误的环境变量
        _llm_instance = HelloAgentsLLM(
            provider="modelscope",
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            model=settings.llm_model
        )
        
        print(f"✅ LLM服务初始化成功")
        print(f"   提供商: {_llm_instance.provider}")
        print(f"   模型: {_llm_instance.model}")
        print(f"   Base URL: {_llm_instance.base_url}")
        print(f"   API Key: {_llm_instance.api_key[:10]}...")
    
    return _llm_instance


def reset_llm():
    """重置LLM实例(用于测试或重新配置)"""
    global _llm_instance
    _llm_instance = None

