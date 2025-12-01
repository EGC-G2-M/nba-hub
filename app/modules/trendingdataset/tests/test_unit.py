from datetime import datetime, timedelta
from app.modules.auth.models import User
from app.modules.dataset.models import DSDownloadRecord, DataSet, PublicationType, DSMetaData
from app.modules.trendingdataset.services import TrendingdatasetService

from app import db
import pytest


@pytest.fixture(scope='module')
def test_client(test_client):
    with test_client.application.app_context():
        user = User(
            email="user@example.com",
            password="testpassword"
        )
        db.session.add(user)
        db.session.commit()

        datasets = []
        for i in range(1, 9):
            meta = DSMetaData(
                title=f"Trending Dataset {i}",
                description=f"A dataset for testing trending datasets {i}.",
                publication_type=(PublicationType.JOURNAL_ARTICLE if i % 2 == 1 else PublicationType.CONFERENCE_PAPER)
            )
            db.session.add(meta)
            db.session.flush()

            ds = DataSet(
                user_id=user.id,
                ds_meta_data_id=meta.id,
                created_at=datetime.utcnow(),
            )
            db.session.add(ds)
            db.session.flush()

            datasets.append((ds, meta))

        now = datetime.utcnow()
        records = []

        # Dataset 1: 3 recent, 1 old
        ds1 = datasets[0][0]
        records.append(DSDownloadRecord(dataset_id=ds1.id, download_date=now - timedelta(days=10), download_cookie="cookie_1a"))
        records.append(DSDownloadRecord(dataset_id=ds1.id, download_date=now - timedelta(days=5), download_cookie="cookie_1b"))
        records.append(DSDownloadRecord(dataset_id=ds1.id, download_date=now - timedelta(days=15), download_cookie="cookie_1c"))
        records.append(DSDownloadRecord(dataset_id=ds1.id, download_date=now - timedelta(days=40), download_cookie="cookie_1d"))

        # Dataset 2: 2 recent
        ds2 = datasets[1][0]
        records.append(DSDownloadRecord(dataset_id=ds2.id, download_date=now - timedelta(days=2), download_cookie="cookie_2a"))
        records.append(DSDownloadRecord(dataset_id=ds2.id, download_date=now - timedelta(days=10), download_cookie="cookie_2b"))

        # Dataset 3: only old downloads
        ds3 = datasets[2][0]
        records.append(DSDownloadRecord(dataset_id=ds3.id, download_date=now - timedelta(days=45), download_cookie="cookie_3a"))

        # Dataset 5: one recent download
        ds5 = datasets[4][0]
        records.append(DSDownloadRecord(dataset_id=ds5.id, download_date=now - timedelta(days=20), download_cookie="cookie_5a"))

        # Dataset 6: one recent and one outside 30 days (so counts as 1 recent)
        ds6 = datasets[5][0]
        records.append(DSDownloadRecord(dataset_id=ds6.id, download_date=now - timedelta(days=31), download_cookie="cookie_6a"))
        records.append(DSDownloadRecord(dataset_id=ds6.id, download_date=now - timedelta(days=3), download_cookie="cookie_6b"))

        # Dataset 8: one recent download
        ds8 = datasets[7][0]
        records.append(DSDownloadRecord(dataset_id=ds8.id, download_date=now - timedelta(days=1), download_cookie="cookie_8a"))

        db.session.add_all(records)
        db.session.commit()

    yield test_client

def test_get_top5_trending_datasets_last_30_days(test_client):

    trending_service = TrendingdatasetService()
    result = trending_service.get_top5_trending_datasets_last_30_days()

    assert len(result) > 0, "No trending datasets found"
    assert result[0][0].ds_meta_data.title == "Trending Dataset 1", "Unexpected dataset title"
    assert result[1][0].ds_meta_data.title == "Trending Dataset 2", "Unexpected dataset title"
    assert result[0][1] == 3, "Unexpected download count"
    assert result[1][1] == 2, "Unexpected download count"
    
def test_no_trending_datasets_outside_30_days(test_client):

    trending_service = TrendingdatasetService()
    result = trending_service.get_top5_trending_datasets_last_30_days()

    for _, download_count in result:
        assert download_count > 0, "Dataset with zero downloads found in trending datasets"
        
def test_trending_datasets_order(test_client):

    trending_service = TrendingdatasetService()
    result = trending_service.get_top5_trending_datasets_last_30_days()

    download_counts = [download_count for _, download_count in result]
    assert download_counts == sorted(download_counts, reverse=True), "Trending datasets are not ordered by download count"

def test_trending_datasets_limit(test_client):

    trending_service = TrendingdatasetService()
    result = trending_service.get_top5_trending_datasets_last_30_days()

    assert len(result) <= 5, "More than 5 trending datasets returned"
    