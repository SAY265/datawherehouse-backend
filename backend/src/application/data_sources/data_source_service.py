"""Application service duy nhất của module Data Source."""

from src.application.data_sources.i_data_source_service import IDataSourceService


class DataSourceService(IDataSourceService):
    """Điểm hiện thực tập trung cho các use case Data Source."""
