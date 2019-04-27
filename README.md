# Init a terralego project

Idea is to create both parts (back & front) with a wonderful python tool called [cookiecutter](https://github.com/audreyr/cookiecutter)

##  Install prerequisites
```
if ! ( virtualenv 2>&1 >/dev/null );then echo "ERROR: install venv, on debian/ubuntu: apt install -y virtualenv,fi";fi
virtualenv --python=python3 ~/tools/cookiecutter
~/tools/cookiecutter/bin/pip install cookiecutter
```

## Create back project

- create on gitlab your project
- then locally (replace with your values)

    ```sh
    cd ~/.cookiecutters/cookiecutter-terra-back \
        && git fetch origin && git reset --hard origin/master \
        && cd -
    cookiecutter --no-input -f -o ~/out_dir \
        https://github.com/Terralego/cookiecutter-terra-back.git \
        tld_domain=makina-corpus.net name=Oppm \
        git_ns=Terralego/Customers/Oppm \
        dev_port=40001 staging_port=40003 qa_port=40005 prod_port=40010
    cd ~/out_dir
    git push origin HEAD:starter
    # for relative checkout to work, we need remote objects locally
    git fetch
    git submodule add -f ../../../../Terralego/Core/terra-back.git lib/terra-back
    git commit local -m "Add deploy"
    ```

## Fill ansible inventory

### Generate ssh deploy key
```ssh
cd local
ssh-keygen -t rsa -b 2048 -N '' -C deploy -f deploy
```

### Generate vaults password file
```sh
export CORPUSOPS_VAULT_PASSWORD=SuperVerySecretPassword
.ansible/scripts/setup_vaults.sh
```

- Also add that variable ``CORPUSOPS_VAULT_PASSWORD`` in the gitlab CI/CD variables
- You would certainly also add ``REGISTRY_USER`` & ``REGISTRY_PASSWORD``.

### Move vault templates to their encrypted counterparts
For each file which needs to be crypted
```sh
# to find them
find .ansible/inventory/group_vars/|grep encrypt
```

### Generate vaults
You need to
1. open in a editor: 

    ```sh
    $EDITOR .ansible/inventory/group_vars/dev/default.movemetoencryptedvault.yml
    ```
2. In another window/shell, use Ansible vault to create/edit that file without the "encrypted" in the filename and 
copy/paste/adapt the content 

    ```sh
    .ansible/scripts/edit_vault.sh .ansible/inventory/group_vars/dev/default.yml
    ```
3. Delete the original file

    ```sh
    rm -f .ansible/inventory/group_vars/dev/default.movemetoencryptedvault.yml
    ```

- Wash, rince, repeat for each needing-to-be-encrypted vault.
- ⚠️Please note⚠️: that you will need to put the previously generated ssh deploy key in ```all/default.yml```

## Init dev and and test locally
```sh
./control.sh init  # init conf files
./control.sh build django
./control.sh build  # will be faster as many images are based on django
```

## Push to gitlab
- Push to gitlab and run the dev job until it succeeds
- Trigger the dev image release job until it succeeds


## Deploy manually
- Deploy manually one time to see everything is in place<br/>
  Remember:
    - Your local copy is synced as the working directory on target env (with exclusions, see playbooks)
    - The ``cops_terralego_docker_tag`` controls which docker image is deployed.

    ```
    .ansible/scripts/call_ansible.sh .ansible/playbooks/deploy_key_setup.yml
    .ansible/scripts/call_ansible.sh -vvv .ansible/playbooks/ping.yml -l dev  # or staging
    .ansible/scripts/call_ansible.sh -vvv .ansible/playbooks/app.yml \
         -e "{cops_terralego_docker_tag: dev}" -l dev  # or staging 
    ```

## Update project
You can regenerate at a later time the project
```
local/regen.sh  # and verify new files and updates
```

## Create front project

Redo the same procedure as for back except;
- TODO



