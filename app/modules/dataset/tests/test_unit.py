import uuid
from flask import make_response
import pytest

from app import db
from app.modules.auth.models import User
from app.modules.dataset.models import DataSet, DSDownloadRecord, DSMetaData, Author
from app.modules.dataset.services import DataSetService
from app.modules.dataset.repositories import DataSetRepository
from app.modules.conftest import login, logout
from datetime import datetime


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
    
def create_dummy_dataset(user_id, title, tags, author_names):
    """
    Crea un dataset completo con Metadata y Autores para pruebas.
    Genera un DOI único para poder acceder por la ruta /doi/...
    """
    fake_doi = f"10.1234/{title.lower().replace(' ', '-')}-{str(uuid.uuid4())[:4]}"

    meta = DSMetaData(
        title=title,
        description=f"Description for {title}",
        publication_type="NONE",
        publication_doi="",
        dataset_doi=fake_doi,
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
    
    db.session.refresh(ds)
    return ds

def test_repo_returns_empty_list_if_no_match(test_client):
    """
    Lógica Pura: Si no hay coincidencias, devuelve lista vacía [].
    """
    user = User.query.first() or User(email="t@t.com", password="p").save()
    
    ds = create_dummy_dataset(user.id, "Unique One", "QuantumPhysics", ["Einstein"])
    
    create_dummy_dataset(user.id, "Other One", "Cooking", ["Chef Ramsay"])

    repo = DataSetRepository()
    
    results = repo.get_related_datasets(ds.id, ["QuantumPhysics"], ["Einstein"])

    assert isinstance(results, list)
    assert results == []


def test_repo_logic_ordering_and_limit(test_client):
    """
    Lógica Pura: Verifica que ordena por descargas y limita a 4 resultados.
    """
    user = User.query.first()
    
    main_ds = create_dummy_dataset(user.id, "Main", "CommonTag", ["Me"])

    ds1 = create_dummy_dataset(user.id, "DS1", "CommonTag", ["A"]); ds1.download_count = 10
    ds2 = create_dummy_dataset(user.id, "DS2", "CommonTag", ["B"]); ds2.download_count = 50
    ds3 = create_dummy_dataset(user.id, "DS3", "CommonTag", ["C"]); ds3.download_count = 5
    ds4 = create_dummy_dataset(user.id, "DS4", "CommonTag", ["D"]); ds4.download_count = 20
    ds5 = create_dummy_dataset(user.id, "DS5", "CommonTag", ["E"]); ds5.download_count = 1

    db.session.add_all([ds1, ds2, ds3, ds4, ds5])
    db.session.commit()

    repo = DataSetRepository()
    results = repo.get_related_datasets(main_ds.id, ["CommonTag"], ["Me"])

    assert len(results) == 4

    assert results[0].id == ds2.id
    assert results[0].download_count == 50
    assert results[1].id == ds4.id
    assert ds5 not in results


def test_repo_logic_excludes_self(test_client):
    """
    Lógica Pura: El dataset no debe recomendarse a sí mismo aunque coincidan tags.
    """
    user = User.query.first()
    ds = create_dummy_dataset(user.id, "Selfie", "Mirror", ["Narcissus"])
    
    repo = DataSetRepository()
    results = repo.get_related_datasets(ds.id, ["Mirror"], ["Narcissus"])
    
    assert ds not in results
    assert results == []
    
def test_service_prepares_data_correctly():
    """
    Verifica que el servicio limpia los tags y extrae autores 
    antes de llamar al repositorio. NO toca la base de datos.
    """
    
    from unittest.mock import MagicMock
    mock_repository = MagicMock()
    service = DataSetService()
    service.repository = mock_repository

    mock_dataset = MagicMock()
    mock_dataset.id = 1
    
    mock_dataset.ds_meta_data.tags = " AI , Machine Learning, " 
    
    author1 = MagicMock(); author1.name = "Maria"
    author2 = MagicMock(); author2.name = "Juan"
    mock_dataset.ds_meta_data.authors = [author1, author2]

    mock_repository.find_by_id.return_value = mock_dataset

    service.get_related_datasets(1)

    mock_repository.get_related_datasets.assert_called_once_with(
        1,                         
        ['AI', 'Machine Learning'],
        ['Maria', 'Juan']           
    )
