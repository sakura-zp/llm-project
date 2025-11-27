"""配置管理模块"""

import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加载环境变量
# Pydantic会自动从.env文件读取配置
# 不需要手动调用 load_dotenv()
def _find_and_load_env():
    """检查.env文件是否存在"""
    current_file = Path(__file__)  # app/config.py
    backend_dir = current_file.parent.parent  # backend/
    env_file = backend_dir / ".env"
    
    if env_file.exists():
        print(f"[信息] 找到.env文件: {env_file}")
    else:
        print(f"[警告] 没有找到.env文件: {env_file}")
        print(f"[提示] 请确保.env文件存在于: {backend_dir}")

_find_and_load_env()

# 获取.env文件路径
def _get_env_file():
    current_file = Path(__file__)
    backend_dir = current_file.parent.parent
    return str(backend_dir / ".env")

class Settings(BaseSettings):
    """应用配置"""

    # 应用基本配置
    app_name: str = "HelloAgents智11能旅行助手"
    app_version: str = "1.0.0"
    debug: bool = False

    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS配置 - 使用字符串,在代码中分割
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"

    # 高德地图 API配置
    amap_api_key: str = "e7a4bd85a8e3b30245af219edb132cdd"

    # Unsplash API配置
    unsplash_access_key: str = "ZNgp5kxj1uMGaj-KHc0STfwlYf2hVGwUq5ZYFZcNhME"
    unsplash_secret_key: str = "9K1D5RZClJAVZi9hejcCijQ5sM29NRr7NdB__-K7gHc"

    # LLM配置 (从.env文件读取)
    llm_api_key: str = "ms-6a3dc416-9f5f-41c0-9715-716b67d61e87"  # 对应 LLM_API_KEY
    llm_base_url: str = "https://api-inference.modelscope.cn/v1"  # 对应 LLM_BASE_URL
    llm_model: str = "Qwen/Qwen2.5-7B-Instruct"  # 对应 LLM_MODEL_ID，使用7B小模型对MCP工具调用支持更好

   

    # 日志配置
    log_level: str = "INFO"

    class Config:
        env_file = _get_env_file()
        case_sensitive = False
        extra = "ignore"  # 忽略额外的环境变量

    def get_cors_origins_list(self) -> List[str]:
        """获取CORS origins列表"""
        return [origin.strip() for origin in self.cors_origins.split(',')]


# 创建全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings


# 验证必要的配置
def validate_config():
    """验证配置是否完整"""
    errors = []
    warnings = []

    if not settings.amap_api_key:
        errors.append("AMAP_API_KEY未配置")

    # HelloAgentsLLM会自动从LLM_API_KEY读取,不强制要求OPENAI_API_KEY
    llm_api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not llm_api_key:
        warnings.append("LLM_API_KEY或OPENAI_API_KEY未配置,LLM功能可能无法使用")

    if errors:
        error_msg = "配置错误:\n" + "\n".join(f"  - {e}" for e in errors)
        raise ValueError(error_msg)

    if warnings:
        print("\n⚠️  配置警告:")
        for w in warnings:
            print(f"  - {w}")

    return True


# 打印配置信息(用于调试)
def print_config():
    """打印当前配置(隐藏敵感信息)"""
    print(f"应用名称: {settings.app_name}")
    print(f"版本: {settings.app_version}")
    print(f"服务器: {settings.host}:{settings.port}")
    print(f"高德地图 API Key: {'已配置' if settings.amap_api_key else '未配置'}")

    # 检查 LLM 配置 - 优先使用新字段，再使用旧字段
    llm_api_key = settings.llm_api_key 
    llm_base_url = settings.llm_base_url 
    llm_model = settings.llm_model 

    print(f"LLM API Key: {'已配置' if llm_api_key else '未配置'}")
    print(f"LLM Base URL: {llm_base_url}")
    print(f"LLM Model: {llm_model}")
    print(f"日志级别: {settings.log_level}")

