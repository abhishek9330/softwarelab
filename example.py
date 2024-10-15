import os

# Disable HTTPS requirement in development (use with caution)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from webapp import WebApp              
from pages.google_drive import GoogleDrivePage       
from pages.google_drive import GoogleDriveCallbackPage       
from pages.db_upload import UploadPage     
from pages.db_home import DbHome
from pages.lab_connection import LabConnection
from pages.download import DownloadPage

app = WebApp(title="Database App")

app.add_page(DbHome())
# app.add_page(GoogleDrivePage())
# app.add_page(GoogleDriveCallbackPage())
app.add_page(LabConnection())
app.add_page(DownloadPage())

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
