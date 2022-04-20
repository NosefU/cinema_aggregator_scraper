# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, text
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from db import db_engine_factory

engine = db_engine_factory()

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base(bind=engine)
metadata = Base.metadata


class Fedmovie(Base):
    """
    Модель фильма, с данными из Реестра прокатных удостоверений фильмов Минкульта РФ
    https://opendata.mkrf.ru/opendata/7705851331-register_movies/
    """
    __tablename__ = 'fedmovie'

    id = Column(Integer, primary_key=True)
    cardNumber = Column(String(20), nullable=False)
    foreignName = Column(String)
    filmname = Column(String, nullable=False, index=True)
    studio = Column(String)
    crYearOfProduction = Column(String, index=True)
    director = Column(String)
    scriptAuthor = Column(String)
    composer = Column(String)
    durationMinute = Column(Integer)
    durationHour = Column(Integer)
    ageCategory = Column(String)
    annotation = Column(Text)
    countryOfProduction = Column(String)
    ageLimit = Column(Integer)
    posterPath = Column(String, server_default=text("''::character varying"))

    def __repr__(self):
        return f'Fedmovie(id={self.id}, {self.filmname}, {self.crYearOfProduction})'


class Theater(Base):
    """
    Модель кинотеатра
    """
    __tablename__ = 'theater'

    id = Column(Integer, primary_key=True, server_default=text("nextval('theater_id_seq'::regclass)"))
    name = Column(String, nullable=False)
    address = Column(String)
    scraper_config = Column(JSON)
    city = Column(String, index=True)
    scraper = Column(String, nullable=False)


class MovieSession(Base):
    """
    Модель киносеанса
    """
    __tablename__ = 'session'
    __table_args__ = (
        UniqueConstraint('theater_id', 'movie_id', 'hall', 'datetime'),
    )

    id = Column(Integer, primary_key=True, server_default=text("nextval('session_id_seq'::regclass)"))
    theater_id = Column(ForeignKey('theater.id', ondelete='CASCADE'), nullable=False)
    movie_id = Column(ForeignKey('fedmovie.id', ondelete='CASCADE'), nullable=False)
    hall = Column(String)
    datetime = Column(DateTime, index=True)
    link = Column(String)

    movie = relationship('Fedmovie')
    theater = relationship('Theater')
