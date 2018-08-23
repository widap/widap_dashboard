# West Interconnection Data Analysis Program (WIDAP) Dashboard

## AWS Deploy Instructions.
1. Start bash run.sh in a separate screen.
2. This assumes you have valid credentials to start the app.
3. Login to the notebook at http://ec2-34-214-155-193.us-west-2.compute.amazonaws.com:8000/
4. Set the Google OAuth credentials and callback URL at the Google Credentials Management screen

## Development Instructions
1. All packages are listed in package_list.txt to use with anaconda
2. Alternatively you can use pip to bring in all the dependencies. You can do a pip install -r requirements.txt
3. Set the following env variables:
	i.   OAUTH_CALLBACK_URL
	ii.  OAUTH_CLIENT_SECRET
	iii. OAUTH_CLIENT_ID
4. Ensure you can build the docker spawner image:
	i.  docker build -t am2434/widap:latest .
	ii. export DOCKER_NOTEBOOK_IMAGE="am2434/widap:latest"
5. Run jupyterhub -f jupyter_config.py --log-level=DEBUG
For questions, please email bclimate@stanford.edu and am2434@cornell.edu
