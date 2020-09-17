web: gunicorn KubernetesRestApiAdapter.wsgi --chdir backend --limit-request-line 8188 --log-file -
worker: celery worker --workdir backend --app=KubernetesRestApiAdapter -B --loglevel=info
