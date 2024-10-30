from flask import render_template, request, session, flash, redirect, url_for
import os
import subprocess
import paramiko

class MLProcessing:
    route = '/ml_process'
    endpoint_name = 'ml_process'
    methods = ['GET', 'POST']

    @staticmethod
    def view_func():
        if request.method=="GET":
            models = list_files("/misc/people/idddp/models")
            data_files = list_files("/misc/people/idddp/data")
            return render_template('ml_processing.html', models=models, data_files=data_files)

        if request.method == "POST":
            # Get the selected model and data file path from the form
            model = request.form.get("model")
            data_file_path = request.form.get("data_file")

            # Define the directory where results will be saved
            results_dir = '/misc/people/idddp/results'
            if not os.path.exists(results_dir):
                os.makedirs(results_dir)

            # Based on the selected model, run the appropriate function
            
            result = run_model(data_file_path, model, "/misc/people/idddp/results")
            
            if result:
                print("got it!!!")
            else:
                print("poooh")

            flash(f"Model {model} processed successfully. Results saved to {results_dir}.", "success")
            return redirect(url_for('db_home'))  # Redirect to the same page or results page if needed

def list_files(folder):
        """Connects to the remote server and lists files in the specified folder."""
        files = []
        try:
            # SSH connection setup
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            credentials = session.get('lab_credentials')

            if not credentials:
                flash('No lab machine credentials found. Please connect first.', 'warning')
                return redirect(url_for('lab_connect'))  # Redirect to the lab connection page if no credentials

            host = credentials['host']
            port = credentials['port']
            username = credentials['username']
            password = credentials.get('password')
            key_filename = credentials.get('key_filename')
            # List files in the specified directory

            if key_filename:
                ssh_client.connect(host, port=port, username=username, key_filename=key_filename)
            else:
                ssh_client.connect(host, port=port, username=username, password=password, look_for_keys=False, allow_agent=False)

            stdin, stdout, stderr = ssh_client.exec_command(f'ls {folder}')
            files = stdout.read().decode().splitlines()
            
            # Close the SSH connection
            ssh_client.close()

        except Exception as e:
            print(f"Error: {e}")
        return files        

def run_model(data_file_path, model, results_dir):
    model_location = f"/misc/people/idddp/models/{model}"
    conda_env_name = "dist_new"  # Replace with your environment name

    try:
        # Use 'bash' shell to activate conda env and then run the Python script
        result = subprocess.run(
            f"source /misc/people/idddp/miniconda3/etc/profile.d/conda.sh && conda activate {conda_env_name} && python3 {model_location} {data_file_path}",
            shell=True, capture_output=True, text=True, check=True, executable="/bin/bash"
        )

        # Log the stdout/stderr for debugging or save them
        print(f"Test model output: {result.stdout}")
        print(f"Test model errors (if any): {result.stderr}")

        # Optionally save the output of the model run in a file within results_dir
        output_file = os.path.join(results_dir, f'{data_file_path}_{model}.txt')
        with open(output_file, 'w') as f:
            f.write(result.stdout)

        return 1

    except subprocess.CalledProcessError as e:
        flash(f"Error running test model: {e.stderr}", "danger")
        print("Error: ", e.stderr)
        return 0
