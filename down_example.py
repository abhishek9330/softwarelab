import os

# Disable HTTPS requirement in development (use with caution)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Set the env variable to disable the scope changed warning
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

from webapp import WebApp              
from pages.google_drive import GoogleDrivePage       
from pages.google_drive import GoogleDriveCallbackPage       
from pages.download import DownloadPage     
from pages.db_home import DbHome

app = WebApp(title="Database App")

app.add_page(DbHome())
app.add_page(GoogleDrivePage())
app.add_page(GoogleDriveCallbackPage())
app.add_page(DownloadPage())

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
