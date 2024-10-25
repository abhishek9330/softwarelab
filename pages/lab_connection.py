from flask import render_template, request, session, redirect, url_for, flash
import paramiko

class LabConnection:
    route = '/lab_connect'  # Set the route for this page
    methods = ['GET', 'POST']
    endpoint_name = 'lab_connect'

    @staticmethod
    def view_func():
        if request.method == 'POST':
            # Get form inputs
            host = request.form.get('host')
            port = int(request.form.get('port'))
            username = request.form.get('username')
            password = request.form.get('password')
            key_filename = request.files['key_filename']

            # Handle private key if provided
            if key_filename.filename == '':
                key_filename = None  # No private key file provided
            else:
                key_filename = key_filename.stream.read()
            # Initialize the SSH connection
            if LabConnection.connect_to_lab_machine(host, port, username, password, key_filename):
                flash('Successfully connected to the lab machine!', 'success')
                next_action = session.get('action')
                return redirect(url_for(next_action))  # Redirect after successful connection
            else:
                flash('Failed to connect. Please check your credentials.', 'danger')

        # Render the connection form (lab_connect.html)
        return render_template('lab_connect.html')

    @staticmethod
    def connect_to_lab_machine(host, port, username, password=None, key_filename=None):
        """Attempts to establish an SSH connection to the lab machine."""
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect using either password or key
            if key_filename:
                ssh_client.connect(host, port=port, username=username, key_filename=key_filename)
            else:
                ssh_client.connect(host, port=port, username=username, password=password, look_for_keys=False, allow_agent=False)

            
            # Store credentials in session
            session['lab_credentials'] = {
                'host': host,
                'port': port,
                'username': username,
                'password': password,
                'key_filename': key_filename
            }

            ssh_client.close()
            return True

        except Exception as e:
            print(f"Connection failed: {e}")
            return False
