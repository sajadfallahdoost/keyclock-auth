import sqlalchemy.orm as so
from conf.alembic import db


class Base(db.BaseMixin, so.MappedAsDataclass):
    """subclasses will be converted to dataclasses"""
    metadata = db.metadata_obj
    __abstract__ = True

