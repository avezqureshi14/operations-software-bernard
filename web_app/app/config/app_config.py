import logging
from functools import lru_cache
from typing import Optional
from pydantic import BaseSettings, Field, BaseModel

# TODO log this into a file
LOG = logging.getLogger("api_db")


class ConfigException(BaseException):
    """ Class to handle exception related to configuration """
    pass


class AppConfig(BaseModel):
    """Fixed Application configuration"""
    _endpoints = {"sections_endpoint": "api/v1/backups/sections/all",
                  "datacenters_endpoint": "api/v1/backups/datacenters/all",
                  "types_endpoint": "api/v1/backups/types/all",
                  "freshness_check_endpoint": "api/v1/backups/check/freshness/all"}

    def get_sections_endpoint(self, host):
        return host + self._endpoints['sections_endpoint']

    def get_datacenters_endpoint(self, host):
        return host + self._endpoints['datacenters_endpoint']

    def get_types_endpoint(self, host):
        return host + self._endpoints['types_endpoint']

    def get_freshness_check_endpoint(self, host):
        return host + self._endpoints['freshness_check_endpoint']


class GlobalConfig(BaseSettings):
    """Global configuration"""
    APP_CONFIG: AppConfig = AppConfig()
    ENV_STATE: Optional[str] = Field(None, env="ENV")

    class Config:
        pass


class DevConfig(GlobalConfig):
    """Development configurations."""
    API_URL = "http://localhost:8282/"
    SECTIONS_API_ENDPOINT = AppConfig().get_sections_endpoint(API_URL)
    DATACENTERS_API_ENDPOINT = AppConfig().get_datacenters_endpoint(API_URL)
    TYPES_API_ENDPOINT = AppConfig().get_types_endpoint(API_URL)
    FRESHNESS_CHECK_API_ENDPOINT = AppConfig().get_freshness_check_endpoint(API_URL)

    class Config:
        env_prefix: str = "DEV_"


class TestConfig(GlobalConfig):
    """Test configurations."""

    class Config:
        env_prefix: str = "TEST_"


class ProdConfig(GlobalConfig):
    """Production configurations."""
    API_URL: Optional[str] = Field(None, env="API_URL")

    class Config:
        env_prefix: str = "PROD_"


class GetConfig:
    """Returns a config instance dependending on the ENV_STATE variable."""

    def __init__(self, env_state: Optional[str]):
        self.env_state = env_state

    def __call__(self):
        if self.env_state == "dev":
            return DevConfig()

        elif self.env_state == "prod":
            return ProdConfig()

        elif self.env_state == "test":
            return TestConfig()

        raise ConfigException('Missing configuration environment')


@lru_cache()
def get_settings() -> BaseSettings:
    LOG.info("Loading config settings from the environment...")
    conf = GetConfig(GlobalConfig().ENV_STATE)()
    return conf
