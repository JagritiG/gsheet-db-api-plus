from sqlalchemy import *
from sqlalchemy.engine import create_engine
from sqlalchemy.schema import *
from sqlalchemy import Table

# Connection and authentication
service_account_file = "service_account_file.json"    # your service account credential file
engine = create_engine('gsheets://', service_account_file=service_account_file, subject='your_business_domain@xx.com')
inspector = inspect(engine)
url = "google_spread_sheet_url"

# Processing
table = Table(
    url,
    MetaData(bind=engine),
    autoload=True)


# delete from Google spreadsheet

# Method: 1
# ex:1:
engine.execute(table.delete().where(table.c.cnt < 3000))

# ex2:
# engine.execute(table.delete().where(table.c.country == "DEN"))

# Method: 2
# ex1:
# stmt = (
#     delete(table).
#     where(table.c.country == 'GER')
# )
# engine.execute(stmt)

# ex2:
# stmt = (
#     delete(table).
#     where(table.c.cnt >= 400)
# )
# engine.execute(stmt)
