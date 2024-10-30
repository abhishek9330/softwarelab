from flask import render_template, request, redirect, url_for, flash, session, after_this_request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
import os
import paramiko
import shutil

class UploadPage:
    route = '/upload'
    upload_folder = os.path.abspath("uploads")
    endpoint_name = 'upload'
    methods = ['GET', 'POST']

    # def __init__(self, web_app):
    #     self.web_app = web_app
    #     # Set the post-auth redirect session value as 'upload'
    #     session['post_auth_redirect'] = 'upload'  # Set upload as the next action after auth

    def allowed_file(self, filename):
        return True
    
    def view_func(self):
        """Handle file upload requests."""
        if request.method == 'POST':
            print("POST request received")  # Debugging output

            # Check if the file part is in the request
            if 'file' not in request.files:
                flash('No file part')
                print("No file part in request")  # Debugging output
                return redirect(request.url)

            file = request.files['file']
            # Check if the user selected a file
            if file.filename == '':
                flash('No selected file')
                print("No file selected")  # Debugging output
                return redirect(request.url)

            # Save and process the file if it's allowed
            if file:
                os.makedirs(self.upload_folder, exist_ok=True)
                filename = os.path.join(self.upload_folder, file.filename)
                print(f"Attempting to save file to: {filename}")
                try:
                    file.save(filename)
                except Exception as e:
                    print("pakda gaya", e)
                print(f"File saved to {filename}")  # Debugging output

                if session['server_type'] == 'gdrive':
                    return self.gdrive(filename, file.filename)
                elif session['server_type'] == 'lab':
                    return self.lab(filename, file.filename)
                elif session['server_type'] == 'aws':
                    return self.aws(filename, file.filename) 
                # keep going for more server_types

        print("Rendering upload form")  # Debugging output
        return render_template('db_upload.html')


    def gdrive(self, file_path, filename):
        """Upload the file to Google Drive."""
        credentials_dict = session.get('credentials')
        
        if not credentials_dict:
            return redirect(url_for('google_drive'))  # Redirect to authentication if credentials are missing

        # Convert the credentials dictionary back into a Credentials object
        credentials = Credentials(**credentials_dict)

        # Check if the file exists before uploading
        if not os.path.exists(file_path):
            flash(f"File not found: {file_path}")
            return redirect(url_for('upload'))

        # Build the Google Drive service with the credentials
        drive_service = build('drive', 'v3', credentials=credentials)

        # Create metadata and media object for upload
        file_metadata = {'name': filename}
        media = MediaFileUpload(file_path, resumable=True)

        # Upload the file to Google Drive
        drive_file = drive_service.files().create(
            body=file_metadata, media_body=media, fields='id').execute()
        # Flash a success message and redirect to the upload page
        flash(f"File uploaded successfully to Google Drive. File ID: {drive_file.get('id')}")

        try:
            os.remove(file_path)
            print(f"File '{file_path}' has been removed from the local system.")
        except Exception as e:
            print(f"Error removing local file '{file_path}': {e}")
            flash(f"File uploaded, but failed to delete locally: {e}", 'warning')

        return redirect(url_for('db_home'))

    
    def lab(self, file_path, filename):
        """
        Upload a file to the lab machine using SSH and return an HTTP response.
        
        :param file_path: Local path to the file being uploaded
        :param filename: The name of the file (as it should appear on the lab machine)
        """
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

        # Hardcoded remote directory
        lab_destination = request.form.get('lab_destination')
        remote_directory = lab_destination
        print(lab_destination)

        # Establish an SSH connection
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect using either password or private key authentication
            if key_filename:
                ssh_client.connect(host, port=port, username=username, key_filename=key_filename)
            else:
                ssh_client.connect(host, port=port, username=username, password=password, look_for_keys=False, allow_agent=False)

            # Open an SFTP session for file upload
            sftp = ssh_client.open_sftp()

            # Define the remote file path where the file will be uploaded
            remote_file_path = os.path.join(remote_directory, filename)

            # Upload the file to the remote machine
            sftp.put(file_path, remote_file_path)
            print(f"File '{filename}' uploaded to '{remote_file_path}' on the lab machine.")
            flash(f"File '{filename}' successfully uploaded to the lab machine.", 'success')

            # Close the SFTP session and SSH connection
            sftp.close()
            ssh_client.close()
            
            try:
                shutil.rmtree(self.upload_folder)
                print(f"File '{file_path}' has been removed from the local system.")
            except Exception as e:
                print(f"Error removing local file '{file_path}': {e}")
                flash(f"File uploaded, but failed to delete locally: {e}", 'warning')

            return redirect(url_for('db_home'))  # Redirect to a success page (or home page)

        except Exception as e:
            print(f"Error during file upload: {e}")
            flash(f"File upload failed: {e}", 'danger')
            return redirect(url_for('upload'))      

    def aws(self, file_path, filename):
        pass
