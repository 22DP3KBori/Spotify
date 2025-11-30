from database import engine
from sqlalchemy import inspect

insp = inspect(engine)

for table_name in insp.get_table_names():
    print("\nTABLE:", table_name)
    for column in insp.get_columns(table_name):
        print("  ", column["name"], column["type"], "nullable=", column["nullable"])