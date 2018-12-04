# Initialise your development environment

All following commands must be run only once at project installation.

## Install docker and docker compose

if you are under debian/ubuntu/mint/centos you can do the following:

```sh
.ansible/scripts/download_corpusops.sh
.ansible/scripts/setup_corpusops.sh
local/*/bin/cops_apply_role --become \
    local/*/*/corpusops.roles/services_virt_docker/role.yml
```

... or follow official procedures for
  [docker](https://docs.docker.com/install/#releases) and
  [docker-compose](https://docs.docker.com/compose/install/).

## First clone

```sh
git clone --recursive git@gitlab.com:dantooin_devs/mixity.git
submodule init --recursive  # only the fist time
git submodule upate
```

## Configuration

Use the wrapper to init configuration files from their ``.dist`` counterpart 
and adapt them to your needs.

```bash
./control.sh init
```

**Hint**: You may have to add `0.0.0.0` to `ALLOWED_HOSTS` in `local.py`.

## Login to the app docker registry

You need to login to our docker registry to be able to use it:

```bash
docker login {{cookiecutter.docker_registry}}  # use your gitlab user
```

**⚠️ See also ⚠️** the makinacorpus doc in the docs/tools/dockerregistry section.

# Use your development environment

## Update submodules

Never forget to grab and update regulary the project submodules:

```sh
git pull
git submodule init --recursive  # only the fist time
git submodule upate
```

## Control.sh helper

You may use the stack entry point helper which has some neat helpers but feel 
free to use docker command if you know what your are doing.

```bash
./control.sh usage # Show all available commands
```

## Start the stack

After a last verification of the files, to run with docker, just type:

```bash
# First time you download the app, or sometime to refresh the image
./control.sh pull # Call the docker compose pull command
./control.sh up # Should be launched once each time you want to start the stack
```

**⚠️ See also ⚠️** the makinacorpus doc in the docs/tools/dockerregistry section.

## Launch app as foreground

```bash
./control.sh fg
```

**⚠️ Remember ⚠️** to use `./control.sh up` to start the stack before.

## Start a shell inside the django container

- for user shell

    ```sh
    ./control.sh usershell
    ```
- for root shell

    ```sh
    ./control.sh shell
    ```

**⚠️ Remember ⚠️** to use `./control.sh up` to start the stack before.

## Rebuild/Refresh local image in dev

```sh
control.sh buildimage
```

## Calling Django manage commands

```sh
./control.sh manage [options]
# For instance:
# ./control.sh manage migrate
# ./control.sh manage shell
# ./control.sh manage createsuperuser
# ...
```

**⚠️ Remember ⚠️** to use `./control.sh up` to start the stack before.

## Run tests

```sh
control.sh tests
# also consider: linting|coverage
```

**⚠️ Remember ⚠️** to use `./control.sh up` to start the stack before.

## Docker volumes

Your application extensivly use docker volumes. From times to times you may 
need to erase them (eg: burn the db to start from fresh)

```sh
docker volume ls  # hint: |grep \$app
docker volume rm $id
```

## Doc for deployment on environments
- [See here](./.ansible/README.md)
