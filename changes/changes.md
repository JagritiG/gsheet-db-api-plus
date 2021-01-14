#### 1. auth.py

```bazaar
Original (BD)
--------------
SCOPES = ['https://spreadsheets.google.com/feeds']
 
# Modified (JG)
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
```

#### 2. db.py
```bazaar
Added by (JG)
----------------
import sqlparse
from gsheetsdb.url import url_from_sql
from gsheetsdb.sqlite import execute_all_sql
```

#### 3. db.py
```bazaar
Original (BD):
--------------
@check_closed
    def execute(self, operation, parameters=None, headers=0):
        self.description = None

        query = apply_parameters(operation, parameters or {})

        try:
            self._results, self.description = execute(
                query, headers, self.credentials)

        except (ProgrammingError, NotSupportedError):
            logger.info('Query failed, running in SQLite')
            self._results, self.description = sqlite_execute(
                query, headers, self.credentials)

        return self
```
```bazaar
Modified by (JG):
-----------------
@check_closed
    def execute(self, operation, parameters=None, headers=0):

        self.description = None
        query = apply_parameters(operation, parameters or {})

        # Use switch cases for select, insert, update, delete (JG)
        # Parse query to extract SQL statement/query type
        parsed = sqlparse.parse(query)[0]
        parsed_token = parsed.tokens

        # Execute only for 'SELECT' query
        if str(parsed_token[0]) == 'SELECT':
            try:
                self._results, self.description = execute(
                query, headers, self.credentials)

            except (ProgrammingError, NotSupportedError):
                logger.info('Query failed, running in SQLite')
                self._results, self.description = sqlite_execute(
                    query, headers, self.credentials)

        # Execute when statement is other than 'SELECT'
        else:
            # Execute all SQL statements other than 'SELECT'
            execute_all_sql(query, headers, self.credentials)
            exit()

        return self
 
```
 #### 4. query.py
 ```bazaar
# import libraries by (JG):
---------------------------
import sqlparse
import re
from gsheetsdb.auth import get_credentials_from_auth

```      

#### 5. sqlite.py
```bazaar
# import libraries by (JG):
--------------------------
import sqlparse
import re
from gsheetsdb.auth import get_credentials_from_auth
from googleapiclient import discovery
from pprint import pprint
from gsheetsdb.url import url_from_sql
from six.moves.urllib import parse
```

#### 6. sqlite.py
```bazaar
Original (BD):
--------------

def execute(query, headers=0, credentials=None):
    # fetch all the data
    from_ = extract_url(query)
    if not from_:
        raise ProgrammingError('Invalid query: {query}'.format(query=query))
    baseurl = get_url(from_, headers)
    payload = run_query(baseurl, 'SELECT *', credentials)

    # create table
    conn = sqlite3.connect(':memory:', detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    create_table(cursor, from_, payload)
    insert_into(cursor, from_, payload)
    conn.commit()

    # run query in SQLite instead
    logger.info('SQLite query: {}'.format(query))
    results = cursor.execute(query).fetchall()
    description = cursor.description

    return results, description
    
```
```bazaar
Modified by (JG):
-----------------
def execute(query, headers=0, credentials=None):

    # fetch all the data
    # Added by (JG)
    # Parse query to extract url
    parsed = sqlparse.parse(query)[0]
    parsed_token = parsed.tokens

    if str(parsed_token[0]) == 'INSERT':

        from_ = parsed_token[4]   # sheet url

    else:
        from_ = extract_url(query)

    if not from_:
        raise ProgrammingError('Invalid query: {query}'.format(query=query))

    baseurl = get_url(from_, headers)
    payload = run_query(baseurl, 'SELECT *', credentials)

    # create table
    conn = sqlite3.connect(':memory:', detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    create_table(cursor, from_, payload)
    insert_into(cursor, from_, payload)

    conn.commit()

    # run query in SQLite instead
    logger.info('SQLite query: {}'.format(query))

    results = cursor.execute(query).fetchall()
    description = cursor.description

    return results, description

```

#### 7. sqlite.py
##### Function to execute sql query other than 'SELECT' and all helper functions:
```bazaar
# Function to execute sql query other than 'SELECT'
def execute_all_sql(query, headers=0, credentials=None):
    """
    Execute INSERT, UPDATE, DELETE.
    :param query: 
    :param headers: 
    :param credentials: 
    :return: 
    """

    # fetch all data
    # get url
    from_ = url_from_sql(query)

    if not from_:
        raise ProgrammingError('Invalid query: {query}'.format(query=query))

    baseurl = get_url(from_, headers)
    payload = run_query(baseurl, 'SELECT *', credentials)

    # create table
    conn = sqlite3.connect(':memory:', detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    create_table(cursor, from_, payload)
    insert_into(cursor, from_, payload)

    # run query in SQLite memory
    logger.info('SQLite query: {}'.format(query))
    cursor.execute(query)

    # Fetch column description and data from sqlite after modification
    stmt = get_col_names(cursor, from_)
    cols = tuple(stmt)

    records = from_sqlite(cursor, from_)
    records.insert(0, cols)

    # Upload records to google spreadsheet
    # retrieve sheet_id and sheet name from url
    sheet_meta = get_sheet_meta(credentials, from_)
    sheet_id = sheet_meta[0]
    sheet_name = sheet_meta[1]

    write_gsheet(credentials, sheet_id, sheet_name, records)
    conn.commit()

    return

```
##### Helper functions:
```bazaar
def from_sqlite(cursor, table):
    """
    Retrieve data from SQLite memory.
    :param cursor: 
    :param table: 
    :return: 
    """

    record = []
    query = 'SELECT * FROM "{table}"'.format(table=table)
    logger.info(query)
    cursor.execute(query)
    result = cursor.fetchall()

    for row in result:
        record.append(row)

    return record

```

```bazaar
def write_gsheet(creds, sheet_id, sheet_name, values):
    """
    Write to google spreadsheet.
    :param creds: 
    :param sheet_id: 
    :param sheet_name: 
    :param values: 
    :return: 
    """


    try:
        value_range_body = {
                "majorDimension": "ROWS",
                'values': values
            }

        # Call the Sheets API
        service = discovery.build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()

        # clear the sheet before uploading
        sheet.values().clear(spreadsheetId=sheet_id, range=sheet_name).execute()
        time.sleep(1)

        # upload data into google spreadsheet
        request = sheet.values().update(spreadsheetId=sheet_id, valueInputOption="USER_ENTERED",
                                        range=sheet_name + '!A1', body=value_range_body)
        response = request.execute()

        print("Updating done successfully!")
        pprint(response)

    except Exception as e:
        print("Error: {}".format(e))
        
```

```bazaar
def parse_col(cols):
    """
    Helper function to parse and retrieve column names
    :param cols: 
    :return: 
    """

    parsed_result = []
    parsed_col = re.split('[" ,]', str(cols))
    for e in parsed_col:
        if e is '':
            continue
        else:
            parsed_result.append(e)

    columns = []
    for i in range(0, len(parsed_result)):
        if i % 2:
            continue
        else:
            columns.append(parsed_result[i])

    return columns
    
```
```bazaar
def get_sheet_meta(creds, url):
    """
    Helper function to get goosle sheet metadata.
    :param creds: 
    :param url: 
    :return: 
    """

    # get spreadsheet ID and name
    service = discovery.build('sheets', 'v4', credentials=creds)
    parts = parse.urlparse(url)

    res = dict()
    meta = []
    if parts.path.endswith('/edit'):
        path = parts.path[:-len('/edit')]
        meta.append(path.split('/')[-1])

    # spreadsheet ID
    spreadsheet_id = meta[0]

    # worksheet gid
    if parts.fragment.startswith('gid='):
        gid = parts.fragment[len('gid='):]
        meta.append(gid)

    sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()

    properties = sheet_metadata.get('sheets')
    for i, item in enumerate(properties):
        title = item.get("properties").get('title')
        sheet_id = (item.get("properties").get('sheetId'))
        res[sheet_id] = title

    # get worksheet title
    for key, value in res.items():
        print(key, value)
        if str(key) == str(meta[1]):
            meta.append(value)

    return [meta[0], meta[2]]


```
```bazaar
def get_col_names(cursor, table):
    """
    Helper function to retrieve columns from  SQLite memory table
    :param cursor: 
    :param table: 
    :return: 
    """
    cursor.execute('SELECT * FROM "{table}"'.format(table=table))
    return [member[0] for member in cursor.description]
    
```

#### 8. url.py
##### Added function to extract url from any sql statement
```bazaar
# Function to extract url from any sql statement
def url_from_sql(sql):
    """
    Extract url from any sql statement.
    :param sql: 
    :return: 
    """

    try:
        parsed_sql = re.split('[( , " )]', str(sql))

        for i, val in enumerate(parsed_sql):
            if val.startswith('https:'):
                sql_url = parsed_sql[i]
                return sql_url

    except Exception as e:
        print("Error: {}".format(e))
        
```

