import uuid
from flask import make_response
import pytest

from app import db
from app.modules.auth.models import User
from app.modules.dataset.models import DataSet, DSDownloadRecord, DSMetaData
from app.modules.conftest import login, logout


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extiende el fixture test_client definido en conftest para provisionar
    un usuario y un dataset de prueba en la BD.
    Ajusta los campos de DataSet según tu modelo (aquí se usa user_id como mínimo).
    """
    with test_client.application.app_context():
        user = User(email="tester@example.com", password="pass1234")
        db.session.add(user)
        db.session.commit()

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


        ds = DataSet(user_id=user.id, ds_meta_data_id=meta.id)
        db.session.add(ds)
        db.session.commit()

        test_client.test_dataset = ds
        test_client.test_dataset_id = ds.id
    yield test_client

def test_download_creates_record_and_increments(test_client):
    ds = test_client.test_dataset

    def mock_send_from_directory(*args, **kwargs):
        return make_response(("ok", 200))
    test_client.application.view_functions["dataset.send_from_directory"] = mock_send_from_directory

    resp = test_client.get(f"/dataset/download/{ds.id}")
    assert resp.status_code == 200

    resp_count = test_client.get(f"/datasets/{ds.id}/stats")
    assert resp_count.status_code == 200, f"Error en count: {resp_count.data}"
    count = resp_count.json["download_count"]
    assert count == 1, f"Se esperaba 1 DSDownloadRecord, hay {count}"

    
def test_download_exist_record_and_not_increments(test_client):
    ds = test_client.test_dataset

    def mock_send_from_directory(*args, **kwargs):
        return make_response(("ok", 200))
    test_client.application.view_functions["dataset.send_from_directory"] = mock_send_from_directory

    test_cookie = str(uuid.uuid4())
    test_client.set_cookie("download_cookie", test_cookie)

    rec = DSDownloadRecord(user_id=None, dataset_id=ds.id, download_cookie=test_cookie)
    db.session.add(rec)
    db.session.commit()

    resp = test_client.get(f"/dataset/download/{ds.id}")
    assert resp.status_code == 200

    resp_count = test_client.get(f"/datasets/{ds.id}/stats")
    assert resp_count.status_code == 200, f"Error en count: {resp_count.data}"
    count = resp_count.json["download_count"]
    assert count == 1, f"El contador no debe incrementarse, sigue siendo {count}"

def test_download_file_and_increment(test_client):
    ds = test_client.test_dataset
    file_id = ds.id

    def mock_download(*args, **kwargs):
        return make_response(("ok", 200))

    test_client.application.view_functions["dataset.send_from_directory"] = mock_download

    test_cookie = str(uuid.uuid4())
    test_client.set_cookie("download_cookie", test_cookie)

    resp = test_client.get(f"/dataset/download/{file_id}")
    assert resp.status_code == 200, f"Error en descarga: {resp.data}"

    resp_count = test_client.get(f"/datasets/{file_id}/stats")
    assert resp_count.status_code == 200
    count = resp_count.json["download_count"]
    assert count == 2, f"El contador debe ser 2 tras otra descarga, es {count}"

def test_download_file_exist_record_and_not_increment(test_client):
    ds = test_client.test_dataset
    file_id = ds.id

    def mock_download(*args, **kwargs):
        return make_response(("ok", 200))

    test_client.application.view_functions["dataset.send_from_directory"] = mock_download

    test_cookie = str(uuid.uuid4())
    test_client.set_cookie("download_cookie", test_cookie)

    rec = DSDownloadRecord(user_id=None, dataset_id=ds.id, download_cookie=test_cookie)
    db.session.add(rec)
    db.session.commit()

    resp = test_client.get(f"/dataset/download/{file_id}")
    assert resp.status_code == 200, f"Error en descarga: {resp.data}"

    resp_count = test_client.get(f"/datasets/{file_id}/stats")
    assert resp_count.status_code == 200
    count = resp_count.json["download_count"]
    assert count == 2, f"El contador no debe incrementarse, sigue siendo {count}"
