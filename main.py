from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, Field, create_engine, Session, select

connect_args = {"check_same_thread": False}
engine = create_engine(
    "sqlite:///movies_db.sqlite",
    echo=True,
    connect_args=connect_args,
)
SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


app = FastAPI()


class MovieBase(SQLModel):
    name: str
    year: int
    note: str | None = Field(default=None)


class Movie(MovieBase, table=True):
    __tablename__ = "movies"

    id: int | None = Field(default=None, primary_key=True)


class MovieCreate(MovieBase):
    pass


class MoviePublic(MovieBase):
    id: int


@app.on_event("startup")
def startup():
    SQLModel.metadata.create_all(engine)


@app.get("/movies", response_model=list[Movie])
def read_all(
    session: Session = Depends(get_session),
):
    movies = session.exec(select(Movie)).all()

    return movies


@app.get("/movies/{movie_id}", response_model=Movie)
def read_one(
    movie_id: str,
    session: Session = Depends(get_session),
):
    movie = session.get(Movie, movie_id)

    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    return movie


@app.post("/movies", response_model=MoviePublic)
def create_one(
    movie: MovieCreate,
    session: Session = Depends(get_session),
):
    db_movie = Movie.model_validate(movie)
    session.add(db_movie)
    session.commit()
    session.refresh(db_movie)

    return db_movie


@app.delete("/movies/{movie_id}")
def delete_one(
    movie_id: str,
    session: Session = Depends(get_session),
):
    movie = session.get(Movie, movie_id)

    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    session.delete(movie)
    session.commit()
