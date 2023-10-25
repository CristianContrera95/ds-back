# ML Platform
*********************

## API - EndPoints

This part of the documentation covers all the interfaces of **ml-platform-api**  

### Login - `http://<host:port>/auth/`

This endpoint group allows you, login into ml-platform and keep session while you user the app.

##### Login - `http://<host:port>/auth/token` - POST
This endpoint login a user, and return a token to communicate with ***Models*** endpoints 

- Example request python
``` python
import requests

r = requests.post("http://localhost:8000/auth/token",
                  json={"username": "my-user"
                        "password": "password"
                         }
                 )
print(r.json())
```
> Body fields:
>- **username**: string   
      name|email of user  
>- **password**: string  
    password for given username

-  Example response python
```
{
  "access_token": "eyJhbGciOiJIU...WRtaW4iLCJ",
  "token_type": "bearer"
}
```

##### Current Account - `http://<host:port>/auth/actual_account` - GET
This endpoint return account data using token given from *login* 

- Example request python
``` python
import requests

r = requests.post("http://localhost:8000/auth/actual_account",
                  params={"token": "eyJhbGciOiJIU...WRtaW4iLCJ"}
                 )
print(r.json())
```
> Params fields:
>- **token**: string   
      session token

-  Example response python
```
{
  "username": "my-user"
}
```

### Models - `http://<host:port>/models/`

This endpoint group allows you register, list and use models (notebooks).

> Nota:   
> All endpoints in this section requires pass as header the token to be passed as a header.
> - Example header in python
>``` python
>import requests
>token = "eyJhbGciOiJIU...WRtaW4iLCJ"
>r = requests.get("http://localhost:8000/models",
>                  headers: { Authorization: `Bearer ` + token },
>                 )
>print(r.json())
>```
Let going to omit the headers in the following examples.

##### List - `http://<host:port>/models/` - GET
Get a list of models registered 

- Example request python
``` python
import requests

r = requests.get("http://localhost:8000/models")
print(r.json())
```

-  Example response python
```
[
  {
    name: 'my-model'
    workspace: "www.workspace.com"               # databricks url where notebook is
    notebook_name: "User/pepe_lui/RandomForest"  # Notebook with model
    cluster_name: "Cluster_3"
    parameters: [
      {
        name: "data_input"                      # param name
        default: None                           # only is not file
        is_file: True 
        conn_str: "eyJhbGciOiJIU...WRtaW4iLCJ"  # connection string to datalake
        container_name: "DS-files"              # container in datalake to upload file
        folder: "RandomForest/inputs/           # folder in container (Optional)
      },
      { ... }
    ]
    output_path: 'notebook'                     # dashboard name to export 
    job_id: 0                                   # Databrick Job id
  },
  { ... }
]
```


Continuara..