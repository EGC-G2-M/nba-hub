import uuid
import pytest
from app import db
from app.modules.auth.models import User
from app.modules.dataset.models import DataSet, DSDownloadRecord, DSMetaData, Author
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

def create_full_dataset(user_id, title, tags, author_names, doi_suffix):
    """
    Helper para crear un dataset completo en la DB de test.
    """
    meta = DSMetaData(
        title=title,
        description="Integration test description",
        publication_type="NONE",
        publication_doi="",
        dataset_doi=f"10.1234/{doi_suffix}",
        tags=tags
    )
    db.session.add(meta)
    db.session.flush()

    for name in author_names:
        author = Author(name=name, ds_meta_data_id=meta.id)
        db.session.add(author)

    ds = DataSet(user_id=user_id, ds_meta_data_id=meta.id)
    ds.created_at = datetime.now()
    db.session.add(ds)
    db.session.commit()
    
    return ds

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

def test_get_top5_trending_datasets_last_30_days(test_client, trending_test_data):
    response = test_client.get("/dataset/trending")
    assert response.status_code == 200
    assert b"Trending Dataset 1" in response.data
    assert b"Trending Dataset 2" in response.data
    assert b"Trending Dataset 5" in response.data
    assert b"Trending Dataset 6" in response.data
    assert b"Trending Dataset 8" in response.data
    assert b"Trending Dataset 3" not in response.data
    assert b"Trending Dataset 4" not in response.data
    assert b"Trending Dataset 7" not in response.data    


def test_no_trending_datasets(test_client, clean_database):
    response = test_client.get("/dataset/trending")
    assert response.status_code == 200
    assert b"No trending datasets found" in response.data

def test_view_dataset_shows_related_datasets(test_client):
    """
    Crea 3 datasets (Main, Related, Unrelated) y verifica que en el HTML
    del Main aparecen los relacionados y se excluyen los otros.
    """

    login(test_client, "user@example.com", "1234")
    
    user = User.query.filter_by(email="user@example.com").first()

    main_ds = create_full_dataset(
        user.id, "Main View Dataset", "AI, Tech", ["Author A"], "main-ds"
    )
    
    related_ds = create_full_dataset(
        user.id, "Related One", "AI, Robots", ["Author B"], "rel-ds"
    )
    
    unrelated_ds = create_full_dataset(
        user.id, "Unrelated Cooking", "Food", ["Chef C"], "unrel-ds"
    )

    url = f"/doi/{main_ds.ds_meta_data.dataset_doi}/"
    resp = test_client.get(url)
    
    assert resp.status_code == 200
    
    html = resp.data.decode('utf-8')

    assert "Related Datasets" in html
    assert "Related One" in html
    assert "Unrelated Cooking" not in html


def test_view_dataset_no_related_message(test_client):
    """
    Verifica que si no hay coincidencias, muestra el mensaje 'No related datasets found'.
    """
    login(test_client, "user@example.com", "1234")
    user = User.query.filter_by(email="user@example.com").first()

    lonely_ds = create_full_dataset(
        user.id, "Lonely Dataset", "Quantum-Unique", ["Dr. Solo"], "lonely-ds"
    )

    url = f"/doi/{lonely_ds.ds_meta_data.dataset_doi}/"
    resp = test_client.get(url)
    
    assert resp.status_code == 200
    html = resp.data.decode('utf-8')

    assert "No related datasets found" in html
    assert "card-title" not in html
