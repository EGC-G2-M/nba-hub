from app.modules.trendingdataset.repositories import TrendingdatasetRepository
from core.services.BaseService import BaseService


class TrendingdatasetService(BaseService):
    def __init__(self):
        super().__init__(TrendingdatasetRepository())

    def get_top5_trending_datasets_last_30_days(self):
        return self.repository.get_top5_trending_datasets_last_30_days()
    