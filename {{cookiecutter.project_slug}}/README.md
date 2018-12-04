## Development usage

### Prerequisites:
#### Install docker and docker compose
- if you are under debian/ubuntu/mint/centos you can do the following:

```sh
    .ansible/scripts/download_corpusops.sh
    .ansible/scripts/setup_corpusops.sh
    local/*/bin/cops_apply_role --become \
        local/*/*/corpusops.roles/services_virt_docker/role.yml
```
- or follow procedures for
  [docker](https://docs.docker.com/install/#releases) and
  [docker-compose](https://docs.docker.com/compose/install/).

## Initialise and use your development environment
### git fOo
#### Clone

    ```sh
    git clone --recursive git@gitlab.com:dantooin_devs/mixity.git
    submodule init --recursive  # only the fist time
    git submodule upate
    ```

#### Update
- If your project has submodules, never forget to grab them

    ```sh
    git pull
    git submodule init --recursive  # only the fist time
    git submodule upate
    ```

### django manage wrapper
- The stack entry point helper which has some neat features

    ```
    control.sh usage
    ```

### Configuration
- Use the wrapper to init configuration files from their ``.dist`` counterpart and adapt them to your needs.

    ```bash
    ./control.sh init
    ```
    - Note that You may have to add `0.0.0.0` to `ALLOWED_HOSTS` in `local.py`.
### Login to the app docker registry
- After a last verification of the files, to run with docker, just type :

    ```bash
    docker login registry.gitlab.com  # use your gitlab user
    ```
- See also the
  [project docker registry](https://gitlab.com/dantooin_devs/mixity/container_registry)

### Start the stack
```bash
# First time you download the app, or sometime to refresh the image
./control.sh pull
./control.sh up
```
### Launch app
```bash
./control.sh up  # only first time
./control.sh fg
```
- ⚠️ makinacorpus devs ⚠️: look to docs/tools/dockerregistry section.
### Interactively manipulate the app container
- for user shell

    ```sh
    ./control.sh up  # only first time
    ./control.sh usershell
    ```
- for root shell

    ```sh
    ./control.sh up  # only first time
    ./control.sh shell
    ```

## Rebuild/Refresh local image in dev
```sh
control.sh build
```

### Applying Django migrations

```sh
./control.sh up  # only first time
./control.sh manage migrate
```

### Create superuser
```sh
control.sh up  # only first time
control.sh manage createsuperuser
```

### Run tests
```sh
control.sh up  # only first time
control.sh tests
# also consider: linting|coverage
```

### Docker volumes
- Your application extensivly use docker volumes. From times to times you may need to erase them (eg: burn the db to start from fresh)

    ```sh
    docker volume ls  # hint: |grep \$app
    docker volume help
    docker volume rm $id
    ```

### Doc for deployment on environments
- [See here](./.ansible/README.md)
