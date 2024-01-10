FROM python:3.9
WORKDIR C:\Users\Krzysiek\Desktop\python_docker
COPY .\requirements.txt \python_docker\requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
