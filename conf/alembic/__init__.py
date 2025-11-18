from conf.database.sqlalchemy import SqlAlchemy

# Create a single database instance
db = SqlAlchemy()

# Export commonly used attributes
__all__ = ["db"]