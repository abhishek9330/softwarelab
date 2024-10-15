from flask import render_template, request, session, flash, redirect, url_for
import os
import subprocess

class MLProcessing:
    route = '/ml_process'
    endpoint_name = 'ml_process'
    methods = ['GET', 'POST']

    @staticmethod
    def view_func():
        if request.method == "POST":
            # Get the selected model and data file path from the form
            model = request.form.get("model")
            data_file_path = request.form.get("data_path")

            # Check if the data file exists on the lab machine
            if not os.path.exists(data_file_path):
                flash(f"The specified data path {data_file_path} does not exist.", "danger")
                return redirect(url_for('ml_process'))

            # Define the directory where results will be saved
            results_dir = '/misc/people/idddp/results'
            if not os.path.exists(results_dir):
                os.makedirs(results_dir)

            # Based on the selected model, run the appropriate function
            if model=='test':
                result = run_test(data_file_path, results_dir)
            elif model == "k-means":
                result = run_kmeans(data_file_path, results_dir)
            elif model == "regression":
                result = run_regression(data_file_path, results_dir)
            elif model == "decision_tree":
                result = run_decision_tree(data_file_path, results_dir)
            else:
                flash("Invalid model selection.", "danger")
                return redirect(url_for('ml_process'))
            if result:
                print("got it!!!")
            else:
                print("poooh")

            flash(f"Model {model} processed successfully. Results saved to {results_dir}.", "success")
            return redirect(url_for('db_home'))  # Redirect to the same page or results page if needed

        # If it's a GET request, render the model selection form
        return render_template("ml_processing.html")

def run_test(data_file_path, results_dir):
    model_location = "/misc/people/idddp/models/test.py"
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
        output_file = os.path.join(results_dir, 'test_model_output.txt')
        with open(output_file, 'w') as f:
            f.write(result.stdout)

        return 1

    except subprocess.CalledProcessError as e:
        flash(f"Error running test model: {e.stderr}", "danger")
        print("Error: ", e.stderr)
        return 0

def run_kmeans(data_file_path, results_dir):
    pass

def run_regression(data_file_path, results_dir):
    pass

def run_decision_tree(data_file_path, results_dir):
    pass
