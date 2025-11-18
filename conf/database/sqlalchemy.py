import configparser
import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase


class BaseMixin(DeclarativeBase):
    """Base mixin for all models."""
    pass


class SqlAlchemy:
    def __init__(self, db_name: str = "", debug: bool = False):
        """
        Initialize SQLAlchemy connection object.
        """
        self.engine: Engine = self.create_engine(debug)
        self.BaseMixin = BaseMixin
        self.metadata_obj = BaseMixin.metadata
        # Keep Base for backward compatibility
        self.Base = BaseMixin
        # self.session = self.create_session()  # Uses default values: auto_flush=True, expire_on_commit=False

    @property
    def version(self) -> str:
        """
        Returns SQLAlchemy version.
        """
        return sa.__version__

    # -----------------------------
    # CREATE ENGINE
    # -----------------------------
    def create_engine(self, debug: bool) -> Engine:
        """
        Create SQLAlchemy engine from alembic.ini URL.
        """
        url = self.get_alembic_sql_conn()
        engine = sa.create_engine(
            url=url,
            echo=debug,
            future=True
        )
        return engine

    # -----------------------------
    # CREATE SESSION
    # -----------------------------
    def create_session(
        self,
        auto_flush: bool = True,
        expire_on_commit: bool = False
    ):
        """
        Return a new SQLAlchemy session.
        """
        Session = so.sessionmaker(
            bind=self.engine,
            autoflush=auto_flush,
            expire_on_commit=expire_on_commit,
        )
        return Session

    # -----------------------------
    # READ CONNECTION URL FROM alembic.ini
    # -----------------------------
    def get_alembic_sql_conn(self) -> str:
        """
        Read sqlalchemy.url from alembic.ini file.
        """
        config = configparser.ConfigParser()
        config.read("alembic.ini")
        return config.get("alembic", "sqlalchemy.url")

    # -----------------------------
    # SIMPLE TEST CONNECTION
    # -----------------------------
    def test_connection(self):
        """
        Try connecting to the database.
        """
        try:
            with self.engine.connect() as conn:
                print("✅ Database connection successful!")
                result = conn.execute(sa.text("SELECT 1"))
                print("Test query result:", result.scalar())
        except Exception as e:
            print("❌ Database connection failed:", str(e))
