from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Field, create_engine, Session

app = FastAPI()
engine = create_engine("sqlite:///movies.sqlite")
SQLModel.metadata.create_all(engine)


class Movies(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    name: str
    year: int
    note: str | None = None


@app.get("/movies", response_model=Movies)
def movies(movie_id: str):
    with Session(engine) as session:
        movie = session.get(Movies, movie_id)

    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    return movie
