from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from flask import session, redirect, url_for, request, send_file, render_template, flash
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import os
import zipfile
import paramiko
import stat

class DownloadPage:
    route = '/download'
    download_folder = 'downloads/'  # Folder to store the downloaded files
    endpoint_name = 'download'
    methods = ['GET', 'POST']

    def view_func(self):
        if request.method=="POST":
            server_type = session.get('server_type')
            if server_type == "lab":
                return self.lab()
            elif server_type == 'gdrive':
                return self.gdrive()
            else:
                return "Invalid server type", 400
        return render_template('download.html')

    def gdrive(self):
        # Get the credentials stored in session
        credentials_dict = session.get('credentials')

        if not credentials_dict:
            return redirect(url_for('google_drive'))  # Redirect to authentication if credentials are missing

        # Convert the credentials dictionary back into a Credentials object
        credentials = Credentials(**credentials_dict)
        if credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
                # Save the refreshed credentials back into the session
                session['credentials'] = {
                    'token': credentials.token,
                    'refresh_token': credentials.refresh_token,
                    'token_uri': credentials.token_uri,
                    'client_id': credentials.client_id,
                    'client_secret': credentials.client_secret,
                    'scopes': credentials.scopes
                }
            except Exception as e:
                print(f"Error refreshing token: {e}")
                return None

        # Initialize Google Drive API
        drive_service = build('drive', 'v3', credentials=credentials)

        # Get the folder name from the form submission
        folder_name = request.form.get('folder_name')

        # Search for the folder with the given name in the user's Drive
        files = []
        page_token = None

        while True:
            response = (
                drive_service.files()
                .list(
                    q=f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false",
                    spaces="drive",
                    fields="nextPageToken, files(id, name)",
                    pageToken=page_token,
                )
                .execute()
            )

            for file in response.get("files", []):
                print(f'Found folder: {file.get("name")}, {file.get("id")}')
            
            files.extend(response.get("files", []))  # Append all files to the list
            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break

        if not files:
            return "Folder is empty", 404

        # Create a folder in the local download directory
        local_folder_path = os.path.join(self.download_folder, folder_name)
        if not os.path.exists(local_folder_path):
            os.makedirs(local_folder_path)

        # Download each file within the folder
        folder_id = files[0]['id']  # Assuming the folder ID of the first result

        # Retrieve and download the files within the folder
        files_in_folder = drive_service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="files(id, name, mimeType)"
        ).execute()

        files = files_in_folder.get('files', [])

        for file in files:
            file_id = file['id']
            file_name = file['name']
            mime_type = file['mimeType']

            if mime_type.startswith('application/vnd.google-apps.'):
                # Handle Google Docs Editors files (Docs, Sheets, Slides)
                google_docs_mime_types = {
                    'application/vnd.google-apps.document': 'application/pdf',  # Export Google Docs as PDF
                    'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # Export Sheets as XLSX
                    'application/vnd.google-apps.presentation': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'  # Export Slides as PPTX
                }

                if mime_type in google_docs_mime_types:
                    export_mime_type = google_docs_mime_types[mime_type]
                    request_drive = drive_service.files().export_media(fileId=file_id, mimeType=export_mime_type)
                    file_extension = export_mime_type.split('/')[-1]
                    file_name = f"{file_name}.{file_extension}"
                    file_path = os.path.join(local_folder_path, file_name)

                    with open(file_path, 'wb') as f:
                        downloader = MediaIoBaseDownload(f, request_drive)
                        done = False
                        while not done:
                            status, done = downloader.next_chunk()
                            print(f"Exporting and downloading {file_name}: {int(status.progress() * 100)}% completed.")
            else:
                # Handle binary files (PDFs, images, etc.)
                request_drive = drive_service.files().get_media(fileId=file_id)
                file_path = os.path.join(local_folder_path, file_name)

                with open(file_path, 'wb') as f:
                    downloader = MediaIoBaseDownload(f, request_drive)
                    done = False
                    while not done:
                        status, done = downloader.next_chunk()
                        print(f"Downloading {file_name}: {int(status.progress() * 100)}% completed.")

        # After downloading the folder, zip it
        zip_filename = f"{folder_name}.zip"
        zip_filepath = os.path.join(self.download_folder, zip_filename)

        with zipfile.ZipFile(zip_filepath, 'w') as zipf:
            for root, dirs, files in os.walk(local_folder_path):
                for file in files:
                    zipf.write(os.path.join(root, file), arcname=os.path.relpath(os.path.join(root, file), local_folder_path))

        # Send the zip file as a download
        return send_file(zip_filepath, as_attachment=True)

    def lab(self):
        """
        Download a folder from the lab machine using SSH and SFTP.
        
        :param remote_folder: Path to the folder on the lab machine to download.
        :param local_folder: Path to the local folder where the contents should be saved.
        """
        local_folder = self.download_folder
        remote_folder = request.form.get('folder_name')
        # Retrieve the credentials from session
        credentials = session.get('lab_credentials')

        if not credentials:
            flash('No lab machine credentials found. Please connect first.', 'warning')
            return redirect(url_for('lab_connect'))  # Redirect to the lab connection page if no credentials

        host = credentials['host']
        port = credentials['port']
        username = credentials['username']
        password = credentials.get('password')
        key_filename = credentials.get('key_filename')

        # Establish an SSH connection
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect using either password or private key authentication
            if key_filename:
                ssh_client.connect(host, port=port, username=username, key_filename=key_filename)
            else:
                ssh_client.connect(host, port=port, username=username, password=password)

            # Open an SFTP session for file download
            sftp = ssh_client.open_sftp()

            # Ensure the local folder exists
            if not os.path.exists(local_folder):
                os.makedirs(local_folder)

            # Stack to track directories to be processed
            dirs_to_process = [(remote_folder, local_folder)]

            # Iteratively process directories
            while dirs_to_process:
                current_remote_dir, current_local_dir = dirs_to_process.pop()

                # Ensure the current local directory exists
                if not os.path.exists(current_local_dir):
                    os.makedirs(current_local_dir)

                # List items in the current remote directory
                for item in sftp.listdir_attr(current_remote_dir):
                    remote_item_path = os.path.join(current_remote_dir, item.filename)
                    local_item_path = os.path.join(current_local_dir, item.filename)

                    if stat.S_ISDIR(item.st_mode):  # If it's a directory, add to the stack
                        dirs_to_process.append((remote_item_path, local_item_path))
                    else:  # If it's a file, download it
                        print(f"Downloading file: {remote_item_path} to {local_item_path}")
                        sftp.get(remote_item_path, local_item_path)

            print(f"Folder '{remote_folder}' downloaded to '{local_folder}' successfully.")
            flash(f"Folder '{remote_folder}' successfully downloaded from the lab machine.", 'success')

            # Create a zip file of the downloaded folder
            zip_filename = f"{remote_folder}.zip"
            zip_filepath = os.path.join(local_folder, zip_filename)

            with zipfile.ZipFile(zip_filepath, 'w') as zipf:
                for root, dirs, files in os.walk(local_folder):
                    for file in files:
                        zipf.write(os.path.join(root, file), 
                                   arcname=os.path.relpath(os.path.join(root, file), local_folder))

            # Close the SFTP session and SSH connection
            sftp.close()
            ssh_client.close()

            # Send the zip file as a download
            return send_file(zip_filepath, as_attachment=True)

        except paramiko.SSHException as e:
            print(f"Failed to connect or download files: {e}")
            flash(f"Failed to connect to the lab machine: {e}", 'danger')
            return redirect(url_for('lab_connect'))  
