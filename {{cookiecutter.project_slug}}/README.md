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

## Use your development environment
### git fOo
- If your project has submodules, never forget to grab them

    ```sh
    git submodule init --recursive  # only the fist time
    git submodule upate
    ```

### sbin/manage.sh
The stack entry point helper which has some neat features

```
sbin/control.sh usage
```

### Configuration
- Use the wrapper to init configuration files from their ``.dist`` counterpart and adapt them to your needs.

    ```bash
    ./sbin/control.sh init
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
sbin/control.sh pull
sbin/control.sh up
```
### Launch app
```bash
sbin/control.sh up  # only first time
sbin/control.sh fg
```
- ⚠️ makinacorpus devs ⚠️: look to docs/tools/dockerregistry section.
### Interactively manipulate the app container
- for user shell

    ```sh
    sbin/control.sh up  # only first time
    scripts/control.sh usershell
    ```
- for root shell

    ```sh
    sbin/control.sh up  # only first time
    scripts/control.sh shell
    ```

## Rebuild/Refresh local image in dev
```sh
sbin/control.sh build
```

### Applying Django migrations

```sh
sbin/control.sh up  # only first time
sbin/control.sh manage migrate
```

### Create superuser
```sh
sbin/control.sh up  # only first time
sbin/control.sh manage createsuperuser
```

### Run tests
```sh
sbin/control.sh up  # only first time
sbin/control.sh tests
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
