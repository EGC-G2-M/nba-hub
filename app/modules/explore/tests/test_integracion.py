import pytest
from datetime import datetime, timedelta, timezone
from app import db
from app.modules.auth.models import User
from app.modules.dataset.models import DataSet, DSMetaData, PublicationType
from app.modules.conftest import login, logout


@pytest.fixture(scope="function")
def test_client_with_date_datasets(test_client):
    """
    Crea datasets con diferentes fechas para tests de integración
    """
    dataset_ids = []
    metadata_ids = []
    
    with test_client.application.app_context():
        user = User.query.filter_by(email="user@example.com").first()
        if not user:
            user = User(email="user@example.com", password="1234")
            db.session.add(user)
            db.session.commit()

        # Dataset antiguo (hace 60 días)
        old_date = datetime.now(timezone.utc) - timedelta(days=60)
        meta_old = DSMetaData(
            title="Old Test Dataset",
            description="Dataset from 60 days ago for testing",
            publication_type=PublicationType.SEASON,
            dataset_doi="10.1234/old-test-dataset",
            tags="old, test, integration"
        )
        db.session.add(meta_old)
        db.session.commit()
        metadata_ids.append(meta_old.id)
        
        ds_old = DataSet(
            user_id=user.id,
            ds_meta_data_id=meta_old.id,
            created_at=old_date
        )
        db.session.add(ds_old)
        db.session.commit()
        dataset_ids.append(ds_old.id)

        # Dataset medio (hace 30 días)
        mid_date = datetime.now(timezone.utc) - timedelta(days=30)
        meta_mid = DSMetaData(
            title="Mid Test Dataset",
            description="Dataset from 30 days ago for testing",
            publication_type=PublicationType.PLAYER,
            dataset_doi="10.1234/mid-test-dataset",
            tags="mid, test, integration"
        )
        db.session.add(meta_mid)
        db.session.commit()
        metadata_ids.append(meta_mid.id)
        
        ds_mid = DataSet(
            user_id=user.id,
            ds_meta_data_id=meta_mid.id,
            created_at=mid_date
        )
        db.session.add(ds_mid)
        db.session.commit()
        dataset_ids.append(ds_mid.id)

        # Dataset reciente (hace 5 días)
        recent_date = datetime.now(timezone.utc) - timedelta(days=5)
        meta_recent = DSMetaData(
            title="Recent Test Dataset",
            description="Dataset from 5 days ago for testing",
            publication_type=PublicationType.PLAYOFFS,
            dataset_doi="10.1234/recent-test-dataset",
            tags="recent, test, integration"
        )
        db.session.add(meta_recent)
        db.session.commit()
        metadata_ids.append(meta_recent.id)
        
        ds_recent = DataSet(
            user_id=user.id,
            ds_meta_data_id=meta_recent.id,
            created_at=recent_date
        )
        db.session.add(ds_recent)
        db.session.commit()
        dataset_ids.append(ds_recent.id)

    yield test_client

    # Cleanup
    with test_client.application.app_context():
        DataSet.query.filter(DataSet.id.in_(dataset_ids)).delete(synchronize_session=False)
        DSMetaData.query.filter(DSMetaData.id.in_(metadata_ids)).delete(synchronize_session=False)
        db.session.commit()


# ------------------------- Tests -------------------------

def test_explore_filter_with_start_date(test_client_with_date_datasets):
    """Test de integración: filtrar por fecha de inicio vía POST"""
    login_response = login(test_client_with_date_datasets, "user@example.com", "1234")
    assert login_response.status_code == 200

    # Filtrar datasets creados en los últimos 45 días
    start_date = (datetime.now(timezone.utc) - timedelta(days=45)).strftime("%Y-%m-%d")
    
    response = test_client_with_date_datasets.post(
        "/explore",
        json={
            "query": "",
            "sorting": "newest",
            "publication_type": "any",
            "start_date": start_date,
            "end_date": ""
        },
        content_type="application/json"
    )
    
    assert response.status_code == 200
    data = response.json
    
    titles = [ds["title"] for ds in data]
    assert len(data) == 2, f"Se esperaban 2 datasets, se encontraron {len(data)}"
    assert "Old Test Dataset" not in titles
    assert "Mid Test Dataset" in titles
    assert "Recent Test Dataset" in titles

    logout(test_client_with_date_datasets)


def test_explore_filter_with_end_date(test_client_with_date_datasets):
    """Test de integración: filtrar por fecha final vía POST"""
    login_response = login(test_client_with_date_datasets, "user@example.com", "1234")
    assert login_response.status_code == 200

    # Filtrar datasets creados hace más de 15 días
    end_date = (datetime.now(timezone.utc) - timedelta(days=15)).strftime("%Y-%m-%d")
    
    response = test_client_with_date_datasets.post(
        "/explore",
        json={
            "query": "",
            "sorting": "newest",
            "publication_type": "any",
            "start_date": "",
            "end_date": end_date
        },
        content_type="application/json"
    )
    
    assert response.status_code == 200
    data = response.json
    
    titles = [ds["title"] for ds in data]
    assert len(data) == 2, f"Se esperaban 2 datasets, se encontraron {len(data)}"
    assert "Old Test Dataset" in titles
    assert "Mid Test Dataset" in titles
    assert "Recent Test Dataset" not in titles

    logout(test_client_with_date_datasets)


def test_explore_filter_with_date_range(test_client_with_date_datasets):
    """Test de integración: filtrar por rango de fechas vía POST"""
    login_response = login(test_client_with_date_datasets, "user@example.com", "1234")
    assert login_response.status_code == 200

    # Filtrar datasets creados entre 45 y 15 días atrás
    start_date = (datetime.now(timezone.utc) - timedelta(days=45)).strftime("%Y-%m-%d")
    end_date = (datetime.now(timezone.utc) - timedelta(days=15)).strftime("%Y-%m-%d")
    
    response = test_client_with_date_datasets.post(
        "/explore",
        json={
            "query": "",
            "sorting": "newest",
            "publication_type": "any",
            "start_date": start_date,
            "end_date": end_date
        },
        content_type="application/json"
    )
    
    assert response.status_code == 200
    data = response.json
    
    titles = [ds["title"] for ds in data]
    assert len(data) == 1, f"Se esperaba 1 dataset, se encontraron {len(data)}"
    assert "Mid Test Dataset" in titles
    assert "Old Test Dataset" not in titles
    assert "Recent Test Dataset" not in titles

    logout(test_client_with_date_datasets)


def test_explore_filter_dates_with_query(test_client_with_date_datasets):
    """Test de integración: combinar filtro de fechas con búsqueda"""
    login_response = login(test_client_with_date_datasets, "user@example.com", "1234")
    assert login_response.status_code == 200

    # Buscar "Test" en los últimos 45 días
    start_date = (datetime.now(timezone.utc) - timedelta(days=45)).strftime("%Y-%m-%d")
    
    response = test_client_with_date_datasets.post(
        "/explore",
        json={
            "query": "Test",
            "sorting": "newest",
            "publication_type": "any",
            "start_date": start_date,
            "end_date": ""
        },
        content_type="application/json"
    )
    
    assert response.status_code == 200
    data = response.json
    
    titles = [ds["title"] for ds in data]
    assert len(data) == 2, f"Se esperaban 2 datasets, se encontraron {len(data)}"
    assert all("Test" in title for title in titles)
    assert "Old Test Dataset" not in titles

    logout(test_client_with_date_datasets)


def test_explore_filter_dates_with_publication_type(test_client_with_date_datasets):
    """Test de integración: combinar filtro de fechas con tipo de publicación"""
    login_response = login(test_client_with_date_datasets, "user@example.com", "1234")
    assert login_response.status_code == 200

    # Filtrar PLAYER en los últimos 45 días
    start_date = (datetime.now(timezone.utc) - timedelta(days=45)).strftime("%Y-%m-%d")
    
    response = test_client_with_date_datasets.post(
        "/explore",
        json={
            "query": "",
            "sorting": "newest",
            "publication_type": "player",
            "start_date": start_date,
            "end_date": ""
        },
        content_type="application/json"
    )
    
    assert response.status_code == 200
    data = response.json
    
    assert len(data) == 1, f"Se esperaba 1 dataset, se encontraron {len(data)}"
    assert data[0]["title"] == "Mid Test Dataset"

    logout(test_client_with_date_datasets)


def test_explore_filter_dates_with_sorting_oldest(test_client_with_date_datasets):
    """Test de integración: verificar ordenamiento con filtros de fecha"""
    login_response = login(test_client_with_date_datasets, "user@example.com", "1234")
    assert login_response.status_code == 200

    # Filtrar últimos 45 días y ordenar por más antiguo
    start_date = (datetime.now(timezone.utc) - timedelta(days=45)).strftime("%Y-%m-%d")
    
    response = test_client_with_date_datasets.post(
        "/explore",
        json={
            "query": "",
            "sorting": "oldest",
            "publication_type": "any",
            "start_date": start_date,
            "end_date": ""
        },
        content_type="application/json"
    )
    
    assert response.status_code == 200
    data = response.json
    
    assert len(data) >= 2
    # El primero debería ser el más antiguo (Mid Test Dataset)
    assert data[0]["title"] == "Mid Test Dataset"
    # El último debería ser el más reciente (Recent Test Dataset)
    assert data[-1]["title"] == "Recent Test Dataset"

    logout(test_client_with_date_datasets)


def test_explore_filter_dates_with_sorting_newest(test_client_with_date_datasets):
    """Test de integración: verificar ordenamiento descendente"""
    login_response = login(test_client_with_date_datasets, "user@example.com", "1234")
    assert login_response.status_code == 200

    # Filtrar últimos 45 días y ordenar por más reciente
    start_date = (datetime.now(timezone.utc) - timedelta(days=45)).strftime("%Y-%m-%d")
    
    response = test_client_with_date_datasets.post(
        "/explore",
        json={
            "query": "",
            "sorting": "newest",
            "publication_type": "any",
            "start_date": start_date,
            "end_date": ""
        },
        content_type="application/json"
    )
    
    assert response.status_code == 200
    data = response.json
    
    assert len(data) >= 2
    # El primero debería ser el más reciente (Recent Test Dataset)
    assert data[0]["title"] == "Recent Test Dataset"
    # El último debería ser el más antiguo (Mid Test Dataset)
    assert data[-1]["title"] == "Mid Test Dataset"

    logout(test_client_with_date_datasets)


def test_explore_filter_empty_dates_returns_all(test_client_with_date_datasets):
    """Test de integración: sin fechas devuelve todos los datasets"""
    login_response = login(test_client_with_date_datasets, "user@example.com", "1234")
    assert login_response.status_code == 200

    response = test_client_with_date_datasets.post(
        "/explore",
        json={
            "query": "",
            "sorting": "newest",
            "publication_type": "any",
            "start_date": "",
            "end_date": ""
        },
        content_type="application/json"
    )
    
    assert response.status_code == 200
    data = response.json
    
    # Debería devolver al menos los 3 datasets de prueba
    assert len(data) >= 3

    logout(test_client_with_date_datasets)


def test_explore_filter_invalid_date_format(test_client_with_date_datasets):
    """Test de integración: manejar formato de fecha inválido"""
    login_response = login(test_client_with_date_datasets, "user@example.com", "1234")
    assert login_response.status_code == 200

    response = test_client_with_date_datasets.post(
        "/explore",
        json={
            "query": "",
            "sorting": "newest",
            "publication_type": "any",
            "start_date": "invalid-date",
            "end_date": ""
        },
        content_type="application/json"
    )
    
    # Debe devolver error 400
    assert response.status_code == 400

    logout(test_client_with_date_datasets)


def test_explore_page_loads_with_date_inputs(test_client_with_date_datasets):
    """Test de integración: verificar que la página explore carga correctamente con inputs de fecha"""
    login_response = login(test_client_with_date_datasets, "user@example.com", "1234")
    assert login_response.status_code == 200

    response = test_client_with_date_datasets.get("/explore")
    
    assert response.status_code == 200
    assert b"start_date" in response.data
    assert b"end_date" in response.data
    assert b'type="date"' in response.data

    logout(test_client_with_date_datasets)


def test_explore_filter_complete_workflow(test_client_with_date_datasets):
    """Test de integración: workflow completo de filtrado por fechas"""
    login_response = login(test_client_with_date_datasets, "user@example.com", "1234")
    assert login_response.status_code == 200

    # 1. Verificar página carga
    page_response = test_client_with_date_datasets.get("/explore")
    assert page_response.status_code == 200

    # 2. Hacer búsqueda con todos los filtros
    start_date = (datetime.now(timezone.utc) - timedelta(days=45)).strftime("%Y-%m-%d")
    end_date = (datetime.now(timezone.utc) - timedelta(days=10)).strftime("%Y-%m-%d")
    
    filter_response = test_client_with_date_datasets.post(
        "/explore",
        json={
            "query": "Test",
            "sorting": "oldest",
            "publication_type": "any",
            "start_date": start_date,
            "end_date": end_date
        },
        content_type="application/json"
    )
    
    assert filter_response.status_code == 200
    data = filter_response.json
    
    # 3. Verificar resultados
    assert len(data) == 1
    assert data[0]["title"] == "Mid Test Dataset"
    assert "Test" in data[0]["title"]
    
    # 4. Verificar que tiene la estructura correcta
    assert "id" in data[0]
    assert "created_at" in data[0]
    assert "publication_type" in data[0]

    logout(test_client_with_date_datasets)

