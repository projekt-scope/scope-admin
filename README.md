<div align="center">

![admin-logo](/readme-files/scope-admin-logo.png)
</div>

# scope-admin
<div align="center">

[![scope-admin](https://img.shields.io/badge/scope-admin-rgb(44%2C177%2C226))]()
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
</div>

## Idea
The idea behind scope-admin is to control and monitor the scope-services via a simple and clear dashboard-like web interface.
New services can be easily integrated. The configuration of each service is also visible and manageable via scope-admin.

For this mainly the python `docker-sdk` as well as `config.json` files for each service are used.

Scope-admin is based on [Flask](https://flask.palletsprojects.com/en/1.1.x/) and uses [_traefik_](https://docs._traefik_.io/) for routing, security and as a reverse proxy.


## Prerequisites
* `docker`
* the cloned repository in a folder of your choice
* `make` (not necessary but really helpful)
* (docker-network `docker network create scope-net`)

## Installation

Scope-admin has two modes:
* _Production_
* _Development_

### Production Mode
In this mode _traefik_ will automatically try to generate a certificate for the domain (specified in the `env`-file) with Let's Encrypt. Every traffic will be routed to go over https.

You can start the production mode in with the command
* `make up-prod` or
* `docker-compose --file docker-compose.yml --file docker-compose.production.yml up -d --remove-orphans`

Scope-admin should now be accessible at the domain you specified in the `env`-file. Be sure that the domain is routing to your system correctly. (`https://$DOMAIN`)
You should also be able to connect by using the local ip of your system: `https://ip`

### Development Mode
In this mode _traefik_ will not try to generate a certificate for the domain. Every traffic will be routed to go over http. Also the _traefik_ dashboard will be available at `localhost:8080`.

You can start the development mode in with the command
* `make up` or
* `docker-compose up -d --remove-orphans`

Scope-admin should than be accessible here :

* `http://localhost`

* the _traefik_ dashboard is also accessible in dev mode: `localhost:8080`


#### Security

Currently if you start scope-admin every service as well as scope-admin container is behind a _basicAuth_ middelware. The username and password is saved in the `file-provider.yml`. The default-user is `admin` and the password is `test`. You can add or change users and passwords according to the _traefik_ [documentation](https://doc._traefik_.io/_traefik_/v2.2/middlewares/basicauth/).


### Registration of a new service

To register a new service you can go to `/registration` route of scope-admin. Registration basically clones a existing git into your scope-admin instance and registers it so you are able to control it via the scope-admin interface. To clone a private repository you should use a Access Token and update the url to:

`https://oauth2:token@gitlab.com/scope/project.git`

Instead of `token` add your private Access Token. If the git is public a Access Token is not needed.

### Prepare a service for scope-admin
To use a service easily with scope-admin the service needs to have a `config.json` file as well as a `Dockerfile` in its root folder.

Example `config.json`
```json
{
  "name": "Service Name",
  "tag": "tag-service",
  "version": "1",
  "docker-hub": "False",
  "description": "Short description of the service functions",
  "start-page": "/index.html",
  "environment": {
    "ADMIN_PASSWORD": "passwords or other env vars are possible here"
  },
  "environment_backup": {
    "ADMIN_PASSWORD": "passwords or other env vars are possible here"
  },
  "ports": {
    "3030/tcp": "3030"
  },
  "volumes": {
    "service-name-data": {
      "bind": "/servicevolume",
      "mode": "rw"
    }
  }
}
```

### Use a Docker-image from Docker-Hub

Scope-admin supports also images from docker-hub directly, for this you need to add a folder as well as a `config.json` of the service/image.

Example `config.json`
```json
{
  "name": "Mongo-DB",
  "tag": "mongo-db",
  "docker-hub": "True",
  "docker-hub-image": "mongo",
  "version": "latest",
  "description": "Mongo-db",
  "start-page": "/",
  "environment": {
    "MONGO_INITDB_ROOT_USERNAME": "root",
    "MONGO_INITDB_ROOT_PASSWORD": "example"
  },
  "environment_backup": {
    "MONGO_INITDB_ROOT_USERNAME": "root",
    "MONGO_INITDB_ROOT_PASSWORD": "example"
  },
  "ports": {
    "27017/tcp": "27017"
  },
  "volumes": {}
}
```

The service needs to be added currently by the user in the `service_config.json` as well:
```json
{
  "internal": {
    .....
    ,
    "mongo-db": {
      "core-service": "false"
      "tag": "mongo-db",
    },
    ....
  }
}
```

After that you should restart scope-admin and you should have a new service in the dashboard. When you install this service the corresponding docker-image will be loaded and build.


## Usage

The scope-admin webapp is running internal at port `1234`. After starting the server you should be able to access the web interface at `http://localhost:1234/`  or if you started everything with _traefik_ you can access it at `http://localhost` or `https://$DOMAIN`.

### Dashboard
At the dashboard you can see all services as well as the status of each service. Scope-admin differentiates between internal and external service. Internal services are running on the same host as scope-admin. External Services can run anywhere.

![dashboard](/readme-files/dashboard.png)

### Service View
For each service there is a separate page. On this page you can see the status and you can
* install
* uninstall
* start (restart)
* stop\
the docker-image or the docker-container. You can also change the environment variables for the docker-container as well as the port at which the service is deployed. Currently you have to reinstall the service to update this files.

You can also see the logs of the container to check the current state.

![service-view](/readme-files/service-view.png)

#### Webinterface
If the container has an webinterface you can access this by clicking on the button `webinterface`. This will open a window inside of scope-admin with the service webinterface.

If you want to open the services webinterface in an own tab you can go to
`https://DOMAIN/service-tag` or `http://localhost/service-tag` . _Treafik_ is then rerouting you to the correct service.