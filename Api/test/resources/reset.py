
import sqlalchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

from test.resources.common import RDatabase


def reset_database():
	# noinspection PyProtectedMember
	db_engine = RDatabase.get()._engine
	base = declarative_base()
	metadata = MetaData(db_engine)
	metadata.reflect()
	metadata.drop_all()

	with open("../setup/testdb.psql") as file:
		escaped_sql = sqlalchemy.text(file.read())
		db_engine.execute(escaped_sql)


if __name__ == "__main__":
	reset_database()
