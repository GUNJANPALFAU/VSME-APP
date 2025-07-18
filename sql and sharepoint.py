import pandas as pd
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential
import io
from sqlalchemy import create_engine

# === 🔐 Step 1: SharePoint Authentication ===
sharepoint_url = "https://msfau.sharepoint.com/teams/REP"
folder_path = "Freigegebene Dokumente/vsme uploads"
sp_username = "et28avyf@fauad.fau.de"
sp_password = "Newlife2022"  
# Connect to SharePoint and fetch latest file
ctx = ClientContext(sharepoint_url).with_credentials(UserCredential(sp_username, sp_password))
folder = ctx.web.get_folder_by_server_relative_url(folder_path)
files = folder.files.get().execute_query()
folders = ctx.web.folders.get().execute_query()
for f in folders:
    print(f.properties["ServerRelativeUrl"])

if not files:
    raise Exception("No files found in SharePoint folder!")



latest_file = files[-1]
print(f" Reading file: {latest_file.properties['Name']}")
response = latest_file.open_binary_stream().execute_query()
df = pd.read_excel(io.BytesIO(response.value))
print(" Excel loaded:")
print(df.head())

# === 🔧 Step 2: Azure SQL Connection ===
sql_server = 'vsmesqlserver.database.windows.net'
sql_database = 'vsmedb'               # change if different
sql_username = 'CloudSAc85fe86a'
sql_password = 'Newlife2022'   # the password you used while creating the SQL admin

driver = 'ODBC Driver 18 for SQL Server'
conn_str = f"mssql+pyodbc://{sql_username}:{sql_password}@{sql_server}:1433/{sql_database}?driver={driver.replace(' ', '+')}"

engine = create_engine(conn_str)

# === Step 3: Upload Data to Azure SQL ===
table_name = 'vsme_answers'

try:
    df.to_sql(table_name, con=engine, if_exists='append', index=False)
    print(f" Data inserted into SQL table: {table_name}")
except Exception as e:
    print(f" SQL Insert failed: {e}")
