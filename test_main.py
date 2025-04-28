import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from main import get_session, app, Movie


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_create_movie(client: TestClient):
    response = client.post(
        "/movies/", json={"name": "Matrix", "year": 1999, "note": None}
    )
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Matrix"
    assert data["year"] == 1999
    assert data["note"] is None
    assert data["id"] is not None


def test_read_movie(session: Session, client: TestClient):
    movie = Movie(name="Matrix", year=1999, note=None)
    session.add(movie)
    session.commit()

    response = client.get(f"/movies/{movie.id}")
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == movie.name
    assert data["year"] == movie.year
    assert data["note"] == movie.note
    assert data["id"] == movie.id


def test_read_all_movies(session: Session, client: TestClient):
    movie_1 = Movie(name="Matrix", year=1999, note=None)
    movie_2 = Movie(
        name="Star Wars: Episode I - The Phantom Menace", year=1999, note=None
    )
    session.add(movie_1)
    session.add(movie_2)
    session.commit()

    response = client.get(f"/movies")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0] == {
        "name": movie_1.name,
        "year": movie_1.year,
        "note": movie_1.note,
        "id": movie_1.id,
    }
    assert data[1] == {
        "name": movie_2.name,
        "year": movie_2.year,
        "note": movie_2.note,
        "id": movie_2.id,
    }


def test_delete_movie(session: Session, client: TestClient):
    movie = Movie(name="Matrix", year=1999, note=None)
    session.add(movie)
    session.commit()

    response = client.delete(f"/movies/{movie.id}")

    movie_in_db = session.get(Movie, movie.id)

    assert response.status_code == 200

    assert movie_in_db is None
