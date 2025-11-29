import uuid
import pytest
from app import db
from app.modules.auth.models import User
from app.modules.dataset.models import DataSet, DSDownloadRecord, DSMetaData
from app.modules.conftest import login, logout
from datetime import datetime

@pytest.fixture(scope="function", autouse=True)
def clean_downloads(test_client):
    """
    Limpia registros de descargas antes de cada test.
    """
    with test_client.application.app_context():
        DSDownloadRecord.query.delete()
        db.session.commit()

@pytest.fixture(scope="function")
def test_client(test_client):
    """
    Asegura que exista un usuario de prueba y un Dataset 1.
    """
    with test_client.application.app_context():
        user = User.query.filter_by(email="user@example.com").first()
        if not user:
            user = User(email="user@example.com", password="1234")
            db.session.add(user)
            db.session.commit()

        meta = DSMetaData.query.filter_by(title="Meta test").first()
        if not meta:
            meta = DSMetaData(
                title="Meta test",
                description="Metadata generada para test",
                publication_type="NONE",
                publication_doi="",
                dataset_doi=None,
                tags="test"
            )
            db.session.add(meta)
            db.session.commit()

        dataset = DataSet.query.get(1)
        if not dataset:
            dataset = DataSet(
                id=1,
                user_id=user.id,
                ds_meta_data_id=meta.id,
                created_at=datetime.utcnow()
            )
            db.session.add(dataset)
            db.session.commit()

    return test_client

# ------------------------- Tests -------------------------

def test_download_creates_record_and_increments(test_client):
    login_response = login(test_client, "user@example.com", "1234")
    assert login_response.status_code == 200

    ds = DataSet.query.first()

    download_cookie = str(uuid.uuid4())
    test_client.set_cookie("download_cookie", download_cookie)
    resp = test_client.get(f"/dataset/download/{ds.id}")
    assert resp.status_code == 200

    stats = test_client.get(f"/datasets/{ds.id}/stats")
    assert stats.status_code == 200
    assert stats.json["download_count"] == 1

    logout(test_client)

def test_download_exist_record_and_not_increments(test_client):
    login_response = login(test_client, "user@example.com", "1234")
    assert login_response.status_code == 200

    ds = DataSet.query.first()

    existing_cookie = str(uuid.uuid4())
    rec = DSDownloadRecord(user_id=None, dataset_id=ds.id, download_cookie=existing_cookie)
    db.session.add(rec)
    db.session.commit()

    test_client.set_cookie("download_cookie", existing_cookie)
    resp = test_client.get(f"/dataset/download/{ds.id}")
    assert resp.status_code == 200

    stats = test_client.get(f"/datasets/{ds.id}/stats")
    assert stats.status_code == 200
    assert stats.json["download_count"] == 2

    logout(test_client)

def test_download_file_and_increment(test_client):
    login_response = login(test_client, "user@example.com", "1234")
    assert login_response.status_code == 200

    ds = DataSet.query.first()

    download_cookie = str(uuid.uuid4())
    test_client.set_cookie("download_cookie", download_cookie)
    resp = test_client.get(f"/dataset/download/{ds.id}")
    assert resp.status_code == 200

    stats = test_client.get(f"/datasets/{ds.id}/stats")
    assert stats.status_code == 200
    assert stats.json["download_count"] == 3

    logout(test_client)

def test_download_file_exist_record_and_not_increment(test_client):
    login_response = login(test_client, "user@example.com", "1234")
    assert login_response.status_code == 200

    ds = DataSet.query.first()

    existing_cookie = str(uuid.uuid4())
    rec = DSDownloadRecord(user_id=None, dataset_id=ds.id, download_cookie=existing_cookie)
    db.session.add(rec)
    db.session.commit()

    test_client.set_cookie("download_cookie", existing_cookie)
    resp = test_client.get(f"/dataset/download/{ds.id}")
    assert resp.status_code == 200

    stats = test_client.get(f"/datasets/{ds.id}/stats")
    assert stats.status_code == 200
    assert stats.json["download_count"] == 4

    logout(test_client)
