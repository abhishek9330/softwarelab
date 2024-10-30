from setuptools import setup, find_packages

setup(
    name="softwarelab",  # Replace with your library's name
    version="1.0.0",
    author="Abhishek Choudhary",
    author_email="abhishek.choudhary@iitb.ac.in",
    description="A library to create webapps with ease",
    url="https://github.com/abhishek9330/softwarelab",
    packages=find_packages(),  # Automatically finds and includes packages
    install_requires=[  # List any dependencies
        # e.g., 'numpy', 'pandas'
        "flask",
        "google-auth", "google-auth-oauthlib", "google-auth-httplib2","google-api-python-client",
        "paramiko"

    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Update if using a different license
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Define the Python version requirement
)
