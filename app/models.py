from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()


class KnsbPlayer(Base):
    __tablename__ = 'knsb_player'

    knsb_id = Column(Integer, primary_key=True)
    fide_id = Column(Integer, index=True, nullable=True)
    name = Column(String)
    title = Column(String, nullable=True)
    fed = Column(String)
    birthyear = Column(Integer)
    sex = Column(String)


class KnsbRating(Base):
    __tablename__ = 'knsb_rating'

    knsb_id = Column(Integer, primary_key=True)
    date = Column(Date, primary_key=True)
    title = Column(String, nullable=True)
    standard_rating = Column(Integer, nullable=True)
    standard_games = Column(Integer, nullable=True)
    rapid_rating = Column(Integer, nullable=True)
    rapid_games = Column(Integer, nullable=True)
    blitz_rating = Column(Integer, nullable=True)
    blitz_games = Column(Integer, nullable=True)
    junior_rating = Column(Integer, nullable=True)
    junior_games = Column(Integer, nullable=True)


class FidePlayer(Base):
    __tablename__ = 'fide_player'

    fide_id = Column(Integer, primary_key=True)
    name = Column(String)
    title = Column(String, nullable=True)
    woman_title = Column(String, nullable=True)
    other_titles = Column(String, nullable=True)
    fed = Column(String)
    birthyear = Column(Integer)
    sex = Column(String)
    active = Column(Boolean)


class FideRating(Base):
    __tablename__ = 'fide_rating'

    fide_id = Column(Integer, primary_key=True)
    date = Column(Date, primary_key=True)

    active = Column(Boolean)

    title = Column(String, nullable=True)
    woman_title = Column(String, nullable=True)
    other_titles = Column(String, nullable=True)

    standard_rating = Column(Integer, nullable=True)
    standard_games = Column(Integer, nullable=True)
    standard_k = Column(Integer, nullable=True)

    rapid_rating = Column(Integer, nullable=True)
    rapid_games = Column(Integer, nullable=True)
    rapid_k = Column(Integer, nullable=True)

    blitz_rating = Column(Integer, nullable=True)
    blitz_games = Column(Integer, nullable=True)
    blitz_k = Column(Integer, nullable=True)


class SuggestPlayer(Base):
    __tablename__ = 'suggest_player'

    id = Column(Integer, primary_key=True)
    knsb_id = Column(Integer, index=True, nullable=True)
    fide_id = Column(Integer, index=True, nullable=True)
    comma_name = Column(String)
    full_name = Column(String)


sqlite_file_name = 'instance/database.db'
sqlite_url = f'sqlite:///{sqlite_file_name}'

connect_args = {'check_same_thread': False}
engine = create_engine(sqlite_url, connect_args=connect_args)
Base.metadata.create_all(bind=engine)

def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
