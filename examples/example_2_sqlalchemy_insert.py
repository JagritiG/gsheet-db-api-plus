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

# insert into google spreadsheet

# Method: 1
# engine.execute(table.insert(), column1=value1, column2=value2, ...)
# Example:
engine.execute(table.insert(), country='USA', cnt=3000)


# Method: 2

# stmt = (
#     insert(table).
#     values(column1=value1, column2=value2)
# )
# engine.execute(stmt)



