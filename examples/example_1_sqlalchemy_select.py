from sqlalchemy import *
from sqlalchemy.engine import create_engine
from sqlalchemy.schema import *


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


query = select([func.count(table.columns.cnt)], from_obj=table)
print(query.scalar())


