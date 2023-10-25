# ML Platform API
*********************

This is an API-REST to ML-Platform web.

---

## Quickstart

### Set up

Setup **ml-platform-api** is done in the usual ways. The simplest way is with bash:

Clone repo from GitHub:
``` bash
git clone https://github.com/PiConsulting/ds-back.git
cd ds-back
```

Set permission to scripts:
``` bash
chmod +x scripts/**
```

Now you can use **virtualenv** or **docker** as next lines:

> - **Virtualenv**:
``` bash
./scripts/create_env.sh
./scripts/run.sh
```

> - **docker**:
``` bash
./scripts/build_docker.sh
./scripts/run.sh docker
```
  
Any way **ml-platform-api** will be running on [http://localhost:8000]( http://localhost:8000 ), there you must get a json such as: `{"server": "API ML Platform"}`

---
