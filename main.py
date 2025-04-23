import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, create_engine, Session
from typer import Typer

app = FastAPI()
engine = create_engine("sqlite:///movies.sqlite")
SQLModel.metadata.create_all(engine)


class MovieItem(BaseModel):
    name: str
    year: int
    note: str | None


class Movies(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    name: str
    year: int
    note: str | None = None


@app.get("/movies", response_model=MovieItem)
def movies(movie_id: str):
    with Session(engine) as session:
        movie = session.get(Movies, movie_id)

    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    return movie


cli = Typer(no_args_is_help=True, add_completion=False)


@cli.command()
def run(host: str = "0.0.0.0", port: int = 5678):
    SQLModel.metadata.create_all(engine)
    uvicorn.run("main:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    cli()
