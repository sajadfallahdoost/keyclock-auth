# from sqlalchemy import text
# from sqlalchemy_utils import database_exists
# from sqlalchemy import create_engine

# url = "postgresql+psycopg2://sajad:Sf35741381@localhost:5432/sajad_db"

# engine = create_engine(url, echo=True)

# try:
#     with engine.connect() as conn:
#         print("Connected successfully!")
#         print(conn.execute(text("SELECT 1")).scalar())
        
# except Exception as e:
#     print("Connection failed:", e)
