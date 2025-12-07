import pytest
from app import create_app, db
from app.modules.flamapy import routes as routes_module


class FakeHubfile:
    def __init__(self, path):
        self._path = path

    def get_path(self):
        return self._path


class FakeService:
    def __init__(self, path):
        self._path = path

    def get_by_id(self, file_id):
        return FakeHubfile(self._path)


def test_check_csv_valid(test_client, tmp_path, monkeypatch):
    csv_path = tmp_path / "valid.csv"
    csv_path.write_text(
        "Name,Height,Age,Games,Points per game,Assists per game,Rebounds per game\n"
        "Zach Randolph,2m06,28,81,20.8,11.7,1.8\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(routes_module, "HubfileService", lambda: FakeService(str(csv_path)))

    resp = test_client.get("/flamapy/check_csv/1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get("message") == "Valid CSV file"


def test_check_csv_header_mismatch(test_client, tmp_path, monkeypatch):
    csv_path = tmp_path / "bad_header.csv"
    csv_path.write_text(
        "Name,Altura,Edad\nSome,1m95,30\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(routes_module, "HubfileService", lambda: FakeService(str(csv_path)))

    resp = test_client.get("/flamapy/check_csv/2")
    assert resp.status_code == 400
    data = resp.get_json()
    assert "Header mismatch" in data.get("errors")[0]


def test_check_csv_invalid_height(test_client, tmp_path, monkeypatch):
    csv_path = tmp_path / "bad_height.csv"
    csv_path.write_text(
        "Name,Height,Age,Games,Points per game,Assists per game,Rebounds per game\n"
        "John Doe,195cm,25,10,5.0,1.0,2.0\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(routes_module, "HubfileService", lambda: FakeService(str(csv_path)))

    resp = test_client.get("/flamapy/check_csv/3")
    assert resp.status_code == 400
    data = resp.get_json()
    assert any("Height" in e for e in data.get("errors"))


@pytest.fixture(scope="module")
def test_app():
    """Create a Flask app for testing with the testing config."""
    app = create_app("testing")
    with app.app_context():
        try:
            db.create_all()
        except Exception:
            pass
        yield app
        try:
            db.session.remove()
            db.drop_all()
        except Exception:
            pass


@pytest.fixture(scope="module")
def test_client(test_app):
    with test_app.test_client() as client:
        yield client


def test_check_csv_empty_file(test_client, tmp_path, monkeypatch):
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("", encoding="utf-8")
    monkeypatch.setattr(routes_module, "HubfileService", lambda: FakeService(str(csv_path)))

    resp = test_client.get("/flamapy/check_csv/4")
    assert resp.status_code == 400
    data = resp.get_json()
    assert data.get("errors") == ["Empty file"]


def test_check_csv_col_count_mismatch(test_client, tmp_path, monkeypatch):
    csv_path = tmp_path / "col_mismatch.csv"
    csv_path.write_text(
        "Name,Height,Age,Games,Points per game,Assists per game,Rebounds per game\n"
        "OnlyName,1m90,25\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(routes_module, "HubfileService", lambda: FakeService(str(csv_path)))

    resp = test_client.get("/flamapy/check_csv/5")
    assert resp.status_code == 400
    data = resp.get_json()
    assert any("expected 7 columns" in e for e in data.get("errors"))


def test_check_csv_name_empty_and_integer_float_errors(test_client, tmp_path, monkeypatch):
    csv_path = tmp_path / "multiple_errors.csv"
    csv_path.write_text(
        "Name,Height,Age,Games,Points per game,Assists per game,Rebounds per game\n"
        ",1m80,notint,notint,notfloat,also_not_float,notfloat\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(routes_module, "HubfileService", lambda: FakeService(str(csv_path)))

    resp = test_client.get("/flamapy/check_csv/6")
    assert resp.status_code == 400
    data = resp.get_json()
    errors = data.get("errors")
    assert any("Name is empty" in e for e in errors)
    assert any("Age 'notint' is not a valid integer" in e for e in errors) or any("Games 'notint' is not a valid integer" in e for e in errors)
    assert any("Points per game 'notfloat' is not a valid number" in e for e in errors)


def test_check_csv_service_exception_returns_500(test_client, tmp_path, monkeypatch):
    class ErrorService:
        def get_by_id(self, file_id):
            raise RuntimeError("service failed")

    monkeypatch.setattr(routes_module, "HubfileService", lambda: ErrorService())

    resp = test_client.get("/flamapy/check_csv/7")
    assert resp.status_code == 500
    data = resp.get_json()
    assert "error" in data


def test_valid_endpoint_returns_success(test_client):
    resp = test_client.get("/flamapy/valid/123")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get("success") is True
    assert data.get("file_id") == 123


def test_check_csv_ignores_blank_rows(test_client, tmp_path, monkeypatch):
    # Header + one blank line -> should be considered valid (blank row skipped)
    csv_path = tmp_path / "blank_row.csv"
    csv_path.write_text(
        "Name,Height,Age,Games,Points per game,Assists per game,Rebounds per game\n\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(routes_module, "HubfileService", lambda: FakeService(str(csv_path)))

    resp = test_client.get("/flamapy/check_csv/8")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get("message") == "Valid CSV file"


def test_check_csv_age_empty_allowed(test_client, tmp_path, monkeypatch):
    csv_path = tmp_path / "age_empty.csv"
    csv_path.write_text(
        "Name,Height,Age,Games,Points per game,Assists per game,Rebounds per game\n"
        "Player One,1m95,,82,10.5,2.3,4.1\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(routes_module, "HubfileService", lambda: FakeService(str(csv_path)))

    resp = test_client.get("/flamapy/check_csv/9")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get("message") == "Valid CSV file"


def test_check_csv_allows_additional_columns(test_client, tmp_path, monkeypatch):
    csv_path = tmp_path / "extra_columns.csv"
    csv_path.write_text(
        "Name,Height,Age,Games,Points per game,Assists per game,Rebounds per game,Extra1,Extra2\n"
        "Extra Player,1m88,30,80,12.3,4.5,6.7,foo,bar\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(routes_module, "HubfileService", lambda: FakeService(str(csv_path)))

    resp = test_client.get("/flamapy/check_csv/10")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get("message") == "Valid CSV file"
