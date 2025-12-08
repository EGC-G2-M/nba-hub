import pytest
from datetime import datetime, timedelta, timezone

from app import db
from app.modules.auth.models import User
from app.modules.dataset.models import DataSet, DSMetaData, PublicationType
from app.modules.explore.services import ExploreService


@pytest.fixture(scope="function")
def test_datasets_with_dates(test_client):
    """
    Crea datasets con diferentes fechas para probar el filtrado
    """
    with test_client.application.app_context():
        user = User.query.filter_by(email="tester@example.com").first()
        if not user:
            user = User(email="tester@example.com", password="pass1234")
            db.session.add(user)
            db.session.commit()

        # Dataset antiguo (hace 60 días)
        old_date = datetime.now(timezone.utc) - timedelta(days=60)
        meta_old = DSMetaData(
            title="Old Dataset",
            description="Dataset from 60 days ago",
            publication_type=PublicationType.SEASON,
            dataset_doi="10.1234/old-dataset",
            tags="old, test"
        )
        db.session.add(meta_old)
        db.session.commit()
        
        ds_old = DataSet(
            user_id=user.id, 
            ds_meta_data_id=meta_old.id,
            created_at=old_date
        )
        db.session.add(ds_old)

        # Dataset medio (hace 30 días)
        mid_date = datetime.now(timezone.utc) - timedelta(days=30)
        meta_mid = DSMetaData(
            title="Mid Dataset",
            description="Dataset from 30 days ago",
            publication_type=PublicationType.PLAYER,
            dataset_doi="10.1234/mid-dataset",
            tags="mid, test"
        )
        db.session.add(meta_mid)
        db.session.commit()
        
        ds_mid = DataSet(
            user_id=user.id, 
            ds_meta_data_id=meta_mid.id,
            created_at=mid_date
        )
        db.session.add(ds_mid)

        # Dataset reciente (hace 5 días)
        recent_date = datetime.now(timezone.utc) - timedelta(days=5)
        meta_recent = DSMetaData(
            title="Recent Dataset",
            description="Dataset from 5 days ago",
            publication_type=PublicationType.PLAYOFFS,
            dataset_doi="10.1234/recent-dataset",
            tags="recent, test"
        )
        db.session.add(meta_recent)
        db.session.commit()
        
        ds_recent = DataSet(
            user_id=user.id, 
            ds_meta_data_id=meta_recent.id,
            created_at=recent_date
        )
        db.session.add(ds_recent)

        db.session.commit()

        # Guardar IDs para cleanup
        test_client.test_ds_ids = [ds_old.id, ds_mid.id, ds_recent.id]
        test_client.test_meta_ids = [meta_old.id, meta_mid.id, meta_recent.id]

    yield test_client

    # Cleanup
    with test_client.application.app_context():
        DataSet.query.filter(DataSet.id.in_(test_client.test_ds_ids)).delete(synchronize_session=False)
        DSMetaData.query.filter(DSMetaData.id.in_(test_client.test_meta_ids)).delete(synchronize_session=False)
        db.session.commit()


def test_filter_with_start_date(test_client, test_datasets_with_dates):
    """Test que filtra datasets creados después de una fecha de inicio"""
    with test_client.application.app_context():
        explore_service = ExploreService()
        
        # Filtrar datasets creados en los últimos 45 días
        start_date = (datetime.now(timezone.utc) - timedelta(days=45)).isoformat()
        
        result = explore_service.filter(
            query="",
            start_date=start_date
        )
        
        titles = [ds.ds_meta_data.title for ds in result]
        
        assert len(result) == 2, f"Se esperaban 2 datasets, se encontraron {len(result)}"
        assert "Old Dataset" not in titles, "Old Dataset no debería estar en los resultados"
        assert "Mid Dataset" in titles, "Mid Dataset debería estar en los resultados"
        assert "Recent Dataset" in titles, "Recent Dataset debería estar en los resultados"


def test_filter_with_end_date(test_client, test_datasets_with_dates):
    """Test que filtra datasets creados antes de una fecha final"""
    with test_client.application.app_context():
        explore_service = ExploreService()
        
        # Filtrar datasets creados hace más de 15 días
        end_date = (datetime.now(timezone.utc) - timedelta(days=15)).isoformat()
        
        result = explore_service.filter(
            query="",
            end_date=end_date
        )
        
        titles = [ds.ds_meta_data.title for ds in result]
        
        assert len(result) == 2, f"Se esperaban 2 datasets, se encontraron {len(result)}"
        assert "Old Dataset" in titles, "Old Dataset debería estar en los resultados"
        assert "Mid Dataset" in titles, "Mid Dataset debería estar en los resultados"
        assert "Recent Dataset" not in titles, "Recent Dataset no debería estar en los resultados"


def test_filter_with_date_range(test_client, test_datasets_with_dates):
    """Test que filtra datasets dentro de un rango de fechas"""
    with test_client.application.app_context():
        explore_service = ExploreService()
        
        # Filtrar datasets creados entre 45 y 15 días atrás
        start_date = (datetime.now(timezone.utc) - timedelta(days=45)).isoformat()
        end_date = (datetime.now(timezone.utc) - timedelta(days=15)).isoformat()
        
        result = explore_service.filter(
            query="",
            start_date=start_date,
            end_date=end_date
        )
        
        titles = [ds.ds_meta_data.title for ds in result]
        
        assert len(result) == 1, f"Se esperaba 1 dataset, se encontraron {len(result)}"
        assert "Mid Dataset" in titles, "Solo Mid Dataset debería estar en los resultados"
        assert "Old Dataset" not in titles, "Old Dataset no debería estar en los resultados"
        assert "Recent Dataset" not in titles, "Recent Dataset no debería estar en los resultados"


def test_filter_without_dates_returns_all(test_client, test_datasets_with_dates):
    """Test que sin filtros de fecha devuelve todos los datasets"""
    with test_client.application.app_context():
        explore_service = ExploreService()
        
        result = explore_service.filter(query="")
        
        # Debería devolver al menos los 3 datasets de prueba (puede haber más de otros tests)
        assert len(result) >= 3, f"Se esperaban al menos 3 datasets, se encontraron {len(result)}"


def test_filter_with_dates_and_query(test_client, test_datasets_with_dates):
    """Test que combina filtro de fechas con búsqueda por query"""
    with test_client.application.app_context():
        explore_service = ExploreService()
        
        # Filtrar por "Dataset" en los últimos 45 días
        start_date = (datetime.now(timezone.utc) - timedelta(days=45)).isoformat()
        
        result = explore_service.filter(
            query="Dataset",
            start_date=start_date
        )
        
        titles = [ds.ds_meta_data.title for ds in result]
        
        assert len(result) == 2, f"Se esperaban 2 datasets, se encontraron {len(result)}"
        assert all("Dataset" in title for title in titles), "Todos los resultados deberían contener 'Dataset'"
        assert "Old Dataset" not in titles, "Old Dataset no debería estar (fuera del rango de fechas)"


def test_filter_with_dates_and_publication_type(test_client, test_datasets_with_dates):
    """Test que combina filtro de fechas con tipo de publicación"""
    with test_client.application.app_context():
        explore_service = ExploreService()
        
        # Filtrar por PLAYER en los últimos 45 días
        start_date = (datetime.now(timezone.utc) - timedelta(days=45)).isoformat()
        
        result = explore_service.filter(
            query="",
            start_date=start_date,
            publication_type="player"
        )
        
        titles = [ds.ds_meta_data.title for ds in result]
        
        assert len(result) == 1, f"Se esperaba 1 dataset, se encontraron {len(result)}"
        assert "Mid Dataset" in titles, "Solo Mid Dataset debería cumplir ambos filtros"


def test_filter_with_dates_and_sorting(test_client, test_datasets_with_dates):
    """Test que el ordenamiento funciona correctamente con filtros de fecha"""
    with test_client.application.app_context():
        explore_service = ExploreService()
        
        # Filtrar y ordenar por más antiguo primero
        start_date = (datetime.now(timezone.utc) - timedelta(days=45)).isoformat()
        
        result = explore_service.filter(
            query="",
            start_date=start_date,
            sorting="oldest"
        )
        
        assert len(result) >= 2, "Debería haber al menos 2 datasets"
        
        # Verificar que están ordenados de más antiguo a más reciente
        dates = [ds.created_at for ds in result]
        assert dates == sorted(dates), "Los datasets deberían estar ordenados de más antiguo a más reciente"


def test_filter_empty_date_strings(test_client, test_datasets_with_dates):
    """Test que strings vacíos de fecha no causan errores"""
    with test_client.application.app_context():
        explore_service = ExploreService()
        
        result = explore_service.filter(
            query="",
            start_date="",
            end_date=""
        )
        
        # No debería lanzar error y debería devolver todos los datasets
        assert len(result) >= 3, f"Se esperaban al menos 3 datasets con strings vacíos"


def test_filter_none_dates(test_client, test_datasets_with_dates):
    """Test que valores None en fechas no causan errores"""
    with test_client.application.app_context():
        explore_service = ExploreService()
        
        result = explore_service.filter(
            query="",
            start_date=None,
            end_date=None
        )
        
        # No debería lanzar error y debería devolver todos los datasets
        assert len(result) >= 3, f"Se esperaban al menos 3 datasets con None"