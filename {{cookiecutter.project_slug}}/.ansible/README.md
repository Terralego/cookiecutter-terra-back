## ansible doc

- Remember to verify the ``.ansible/scripts/ansible_deploy_env.local`` content

### the big picture
- The high level infrastructure:

    ```
     ~~~~~~~                                             /\
    / ^   ^ \                  +------------+           //\\
    | 0   0 |                  |  gitlab &  |          /// \\
     \  <   /                  |  gitlab-ci |<--<--<- //~~~~~\
      \____/                   +------------+         / ^   ^ \ -- ~ developers
           \                           |              | 0 < 0 |
            users >---->-- internet ------->------\   \   -  /
             |                         |           \   \____/
    +++++++++++++++++++++++++++++++++++|+++++     +++++++++++++++++++++++++++++++
    +  Preprod Cluster                 |    +     +  Prod Cluster               +
    +     ssh: port: 22                |    +     +   ssh: port 22              +
    +   +--haproxy: port 80/443        |    +     + l +--haproxy: port 80/443   +
    + l +--ssh: 4000x -> LXC ci runner |    +     + x +--ssh: 4000x -> LXC prod +
    + x +--ssh: 4000x -> LXC staging   |    +     + c |10.8.0.1                 +
    + c-+10.8.0.1                      |    +     +   |                         +
    +   |  ++++++++++++++++++++++      |    +     + b |                         +
    + b |  | LXC CI: 10.8.0.x   |<--<--+    +     + r |                         +
    + r |  |   - gitlab runners |           +     + i |                         +
    + i |  ++++++++++++++++++++++           +     + d |                         +
    + d |      CI/CD Runners                +     + g |                         +
    + g |     +--launch deploys via ansible-+->+  + e | ++++++++++++++++++++++  +
    + e | +<--+ after producting docker images |  +   +-| LXC PROD: 10.8.0.x |<--+
    +   | |             |                   +  +->-->-->|    - app in docker |  +|
    +   | |             +->-->-->-->-->-->+ +     +     ++++++++++++++++++++++  +|
    +   | |   +++++++++++++++++++++++++   | +     +                             +|
    +   | +-->| LXC STAGING: 10.8.0.x |   | +     +                             +|
    +   +-----|    - app in docker    |   | +     +                             +|
    +         +++++++++++++++++++++++++   | +     +                             +|
    ++++++++++++++++++++++|+++++++++++++++|++     +++++++++++++++++++++++++++++++|
                          |               |  +-----------------+                 |
                          |               +->| Docker Registry |->-->-->-->-->-->+
                          +-<-<-<-<-<-<-<-<--|                 |
                                             +-----------------+
    ```
- The LXC CI running must be accessible in push from gitlab-ci
- The LXC CI running must be allowed
    - to pull and push from the docker registry
    - to access each lxc deploy env on it's ssh port
- Each deployment LXC host a containerized (docker) deployment
  of the application:

    ```
        LXC---DOCKER
               |
               +--- nginx: main reverse proxy
               |
               +--- django: app
               |            (share a special 'static' & medias volume
               |             nginx which serve the application statis & medias)
               |
               +--- pgsql
               |
               +--- redis
               |
               +--- backup
               +--- ...
    ```

### The CI/CD workflow
- Procedure:
    - Developer develop using his localhost with docker-compose
    - He pushes it's commit to gitlab and The CI/CD pipelines are thrown:
        - Build pipeline:
            - On each build/release step:
                - We ensure login against the target docker registry
                - To speed build builds
                    - we pull if existing the previous docker image
                    - we warm the docker cache by unpackging previous
                      relevant docker images which are in cache (if existing)
                - A new container image is done
                - Tests and other QA jobs are run under the built images
            - Release of everything is still ok:
                - If it is master or a tag, the image is pushed to the registry
                  with the appropriate tag
        - In all cases, we teardown the test resources:
            - test dockers (compose) are downed.
            - If master/tag, TMP image is now a reference image in cache
              to speed up further builds
            - TMP built image is deleted in other cases
        - Deploy steps:
            - We deploy using an ansible playbook who do:
                - Sync code using rsync
                - Generate
                    - each docker env file (.env, docker.env)
                    - Any app settings file
                    - We try a most to put everything as ENV Variables to
                      embrace the 12Factors principle.
                - Pull images
                - Install systemd launcher and start it
                - Restart explcity each docker services
                - Cleanup stale docker volumes
            - For dev or staging if no dev:
                - we autodeploy master and tags
                - we await for manual instruction to deploy any other branch/PR.
            - For other envs than dev/staging, we await for a manual, user,
              instruction to deploy on envs.

### Install log
- [Environments install notes](./log_install.md)

### <a name="download"/>Download corpusops
- Attention local/corpusops.bootstrap folder must be empty for cloning directly inside it.

    ```sh
    .ansible/scripts/download_corpusops.sh
    .ansible/scripts/setup_ansible.sh
    ```

### <a name="setupvault"/>Vault passwords setup
#### <a name="vaultpassword"/>Generate vault password file
- For each environment, setup first the ``vault password file`` that contains your vault password.
  This will create the vaults files ``~/.ansiblevault*env*``

    ```sh
    # Replace here SUPER_SECRET_PASSWORD by the vault password
    # Note the leading " " not to have the password in bash history
     CORPUSOPS_VAULT_PASSWORD='REPLACE_ME_BY_REAL_VAULT_PASSWORD' .ansible/scripts/setup_vaults.sh"
    ```

#### <a name="sshkeyvaultsetup"/>Generate ssh deploy key
- To <a name="sshkeygen"/> generate a ssh keypair if not present inside your secret vault of you want to change it

    ```sh
    export A_ENV_NAME=deploy
    ssh-keygen -t rsa -b 2048 -N '' -C $A_ENV_NAME -f $A_ENV_NAME
    ```

#### <a name="sshkeyvaultsetup"/>Configure ssh keys and other secret in crypted vault
- Use ansible-vault wrapper to create/edit your vault content

    ```sh
    # export A_ENV_NAME=<env>
    .ansible/scripts/edit_vault.sh
    ```

- will open a terminal with your vault and add it then to your crypted vault (``toto.pub``)
   file content in public, and the other in private)

    ```yaml
    cops_deploy_ssh_key_paths:
      # replace by your env id used in the host definition inside your former inventory
      deploy:
        path: "{{'local/.ssh/deploy'|copsf_abspath}}"
        pub: |-
          ssh-rsa xxx
        private: |-
          -----BEGIN RSA PRIVATE KEY-----
          xxx
          -----END RSA PRIVATE KEY-----
    ```
- You just edit the general vault name, but you can setup secret variables for each env this way:

    ```sh
    .ansible/scripts/edit_vault .ansible/inventory/group_vars/$A_ENV_NAME/default.yml
    ```

### <a name="sshdeploysetup"></a>GENERIC ssh setup
- Generate from the vault inventory you just did, the ssh connection keyfile
  for ansible to connect to remote boxes (in ``./local/.ssh``)

    ```sh
    # Generate SSH deploy key locally for ansible to work and dump
    # the ssh key contained in inventory in a place suitable
    # by ssh client (ansible)
    .ansible/scripts/call_ansible.sh .ansible/playbooks/deploy_key_setup.yml
    ```

### Bootstrap env
- [see install log](./log_install.md)

## Cleaning the ci cache on the staging VPS
- when the remaining hard drive space happen to be low
    - connect to the CI runner
    - delete everything inside ``/cache/*``
