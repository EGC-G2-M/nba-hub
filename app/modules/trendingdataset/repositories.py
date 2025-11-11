from app.modules.dataset.models import DataSet, DSMetaData, Author, DSDownloadRecord
from core.repositories.BaseRepository import BaseRepository
from datetime import datetime, timedelta
from sqlalchemy import func


class TrendingdatasetRepository(BaseRepository):
    def __init__(self):
        super().__init__(DataSet)

    def get_top5_trending_datasets_last_30_days(self):
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        trending_datasets = (
            self.session.query(
                DataSet,
                func.count(DSDownloadRecord.id).label('download_count')
            )
            .join(DSDownloadRecord, DSDownloadRecord.dataset_id == DataSet.id)
            .filter(DSDownloadRecord.download_date >= thirty_days_ago)
            .group_by(DataSet.id)
            .order_by(func.count(DSDownloadRecord.id).desc())
            .limit(5)
            .all()
        )
        return trending_datasets
