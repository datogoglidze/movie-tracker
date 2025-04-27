from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, Field, create_engine, Session

database = "sqlite:///movies.sqlite"
engine = create_engine(database)
SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


app = FastAPI()


class Movie(SQLModel, table=True):
    __tablename__ = "movies"

    id: str = Field(default=None, primary_key=True)
    name: str
    year: int
    note: str | None = None


@app.get("/movies", response_model=Movie)
def read_one(movie_id: str, session: Session = Depends(get_session)):
    movie = session.get(Movie, movie_id)

    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    return movie
