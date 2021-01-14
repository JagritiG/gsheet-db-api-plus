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


# Update in Google spreadsheet


# method-1
engine.execute(table.update().where(table.c.country == "USA").values(cnt=55))
# engine.execute(table.update().where(table.c.country == "IND").values(country='DEN'))
# engine.execute(table.update().where(table.c.country == "DEN").values(cnt=1500, quantity=2500))
# engine.execute(table.update().where(table.c.country == "GER").values(country='IND', cnt=8000, quantity=85))
