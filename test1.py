import pandas as pd
import requests
from io import BytesIO
from azure.identity import DefaultAzureCredential
from sqlalchemy import create_engine
import urllib

### === STEP 1: Read file from SharePoint === ###
sharepoint_url = "https://msfau.sharepoint.com/sites/REP/Shared%20Documents/automatedgmbh_1234.csv"

# Use requests to fetch CSV
response = requests.get(sharepoint_url)
if response.status_code != 200:
    raise Exception(f"Failed to fetch SharePoint file: {response.status_code}")

df = pd.read_csv(BytesIO(response.content))

### === STEP 2: Authenticate to Azure SQL === ###
credential = DefaultAzureCredential()
token = credential.get_token("https://database.windows.net/.default").token

# Azure SQL connection details
server = "vsmesqlserver.database.windows.net"      # e.g., gunjanserver.database.windows.net
database = "vsmedb"                      # e.g., vsme
table_name = "automatedgmbh"

# ODBC driver for Azure SQL
driver = "ODBC+Driver+18+for+SQL+Server"

# SQLAlchemy engine with Azure token
connection_url = f"mssql+pyodbc://@{server}/{database}?driver={driver}"
engine = create_engine(
    connection_url,
    connect_args={
        "attrs_before": {1256: bytes(token, "utf-8")}  # 1256 is SQL_COPT_SS_ACCESS_TOKEN
    }
)

### === STEP 3: Upload DataFrame to SQL (creates table automatically) === ###
df.to_sql(name=table_name, con=engine, if_exists="replace", index=False)
print(" Data uploaded successfully!")
