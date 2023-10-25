FROM tiangolo/uvicorn-gunicorn:python3.8-alpine3.10

WORKDIR /workspace
RUN chmod -R a+w /workspace

# Alpine libraries
RUN apk update && apk add gcc g++ libc-dev python3-dev libxml2 libffi-dev openssl-dev curl

# Gunicorn variables
ENV TIMEOUT=300
ENV WORKERS_PER_CORE=4
ENV MAX_WORKERS=16
ENV KEEP_ALIVE=30

# Python libraries
COPY requirements.txt .
RUN pip install --upgrade pip
RUN CRYPTOGRAPHY_DONT_BUILD_RUST=1 pip install --no-cache-dir -r requirements.txt

COPY src .

#EXPOSE 8000
#CMD ["uvicorn", "main:app",  "--port", "8000", "--host", "0.0.0.0", "--reload"]