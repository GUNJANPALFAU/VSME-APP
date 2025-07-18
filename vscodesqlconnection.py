import pyodbc

conn_str = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=vsmesqlserver.database.windows.net;" 
    "Database=vsmedb;"  
    "UID=et28avyf@fauad.fau.de;"           
    "PWD=Newlife2022;"  
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
)

try:
    conn = pyodbc.connect(conn_str)
    print(" Connected successfully!")
except Exception as e:
    print(" Connection failed")
    print(e)
