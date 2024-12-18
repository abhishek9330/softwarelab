import os

# # Disable HTTPS requirement in development (use with caution)
# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# # Set the environment variable to disable the scope changed warning
# os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1''

from webapp import WebApp                  
from pages.db_upload import UploadPage     
from pages.download import DownloadPage
from pages.db_home import DbHome
from pages.lab_connection import LabConnection
from pages.ml_processing import MLProcessing

app = WebApp(title="Database App")

app.add_page(DbHome())
app.add_page(LabConnection())
app.add_page(UploadPage())
app.add_page(DownloadPage())
app.add_page(MLProcessing())

# Run the app
if __name__ == '__main__':
    app.run(debug=True)