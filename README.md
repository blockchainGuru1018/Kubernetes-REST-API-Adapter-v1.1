# Kubernetes-Rest-Api-Adapter


## Running
### Setup
- Create a new virtualenv with either [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) or only virtualenv: `mkvirtualenv KubernetesRestApiAdapter` or `python -m venv KubernetesRestApiAdapter-venv`.
    > If you're using Python's virtualenv (the latter option), make sure to create the environment with the suggested name, otherwise it will be added to version control.
- Create a copy of ``KubernetesRestApiAdapter/settings/local.py.example``:  
  `cp KubernetesRestApiAdapter/settings/local.py.example KubernetesRestApiAdapter/settings/local.py`
- Create a copy of ``.env.example``:
  `cp .env.example .env`
- Create the migrations for `users` app: 
  `python manage.py makemigrations`
- Run the migrations:
  `python manage.py migrate`

### Running the project
- Open a command line window and go to the project's directory.
- `pip install -r requirements.txt && pip install -r dev-requirements.txt`
- `npm install`
- `npm run start`
- Open another command line window.
- activate virtualenv
- Go to the `backend` directory.
- `python manage.py runserver`
