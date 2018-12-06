#!/bin/bash
set -e
W="$(dirname $(readlink -f $0))"

SHELL_DEBUG=${SHELL_DEBUG-${SHELLDEBUG}}
if  [[ -n $SHELL_DEBUG ]];then set -x;fi

shopt -s extglob

APP=django
APP_USER=${APP_USER:-${APP}}
APP_CONTAINER=${APP_CONTAINER:-${APP}}
DEBUG=${DEBUG-}
NO_BACKGROUND=${NO_BACKGROUND-}
BUILD_PARALLEL=${BUILD_PARALLEL:-1}
BUILD_CONTAINERS="cron $APP_CONTAINER"
EDITOR=${EDITOR:-vim}
DIST_FILES_FOLDERS=". src/*/settings"

set_dc() {
    local COMPOSE_FILES="${@:-docker-compose.yml docker-compose-dev.yml}"
    DC=${COMPOSE_COMMAND:-docker-compose}
    for i in $COMPOSE_FILES;do
        DC="${DC} -f $i"
    done
    DCB="$DC -f docker-compose-build.yml"
}

log(){ echo "$@">&2;}

vv() { log "$@";"$@";}

dvv() { if [[ -n $DEBUG ]];then log "$@";fi;"$@";}

_shell() {
    local container="$1" user="$2"
    shift;shift
    local bargs="$@"
    set -- dvv $DC \
        run --rm --no-deps --service-ports \
        -e TERM=$TERM -e COLUMNS=$COLUMNS -e LINES=$LINES \
        -u $user $container bash
    if [[ -n "$bargs" ]];then
        set -- $@ -c "$bargs"
    fi
    "$@"
}

do_usershell() { _shell $APP_CONTAINER $APP_USER $@;}

do_shell()     { _shell $APP_CONTAINER root      $@;}

do_install_docker() {
    vv .ansible/scripts/download_corpusops.sh
    vv .ansible/scripts/setup_corpusops.sh
    vv local/*/bin/cops_apply_role --become \
        local/*/*/corpusops.roles/services_virt_docker/role.yml
}

do_pull() {
    vv $DC pull $@
}

do_up() {
    local bars=$@
    set -- vv $DC up
    if [[ -z $NO_BACKGROUND ]];then bargs="-d $bargs";fi
    $@ $bargs
}

do_down() {
    local bargs=$@
    set -- vv $DC down
    $@ $bargs
}

stop_containers() {
    for i in ${@:-$APP_CONTAINER};do $DC stop $i;done
}

do_runserver() {
    local bargs=${@:-0.0.0.0:8000}
    stop_containers
    do_shell \
    ". ../venv/bin/activate
    && ./manage.py migrate
    && ./manage.py runserver $bargs"
}

do_run_server() { do_runserver $@; }

do_fg() {
    stop_containers
    vv $DC run --rm --no-deps --service-ports $APP_CONTAINER $@
}

do_build() {
    local bargs="$@" bp=""
    if [[ -n $BUILD_PARALLEL ]];then
        bp="--parallel"
    fi
    set -- vv $DCB build $bp
    if [[ -z "$bargs" ]];then
        bargs=$BUILD_CONTAINERS
    fi
    $@ $bargs
}

do_test() {
    local bargs=${@:-tests}
    stop_containers
    set -- vv do_shell \
        "chown django ../.tox
        && gosu django ../venv/bin/tox -c ../tox.ini -e $bargs"
    "$@"
}

do_tests() { do_test $@; }

do_linting() { do_test linting; }

do_coverage() { do_test coverage; }

do_usage() {
    echo "$0:
    install_docker: install docker and docker compose on ubuntu
    init: copy base configuration files from defaults if not existing
    pull [\$args]: pull stack container images
    up [\$args]: start stack
    down [\$args]: down stack
    tests: run tests
    linting: run linting tests
    coverage: run coverage tests
    runserver [\$args]: launch app container in foreground (using django runserver)
    fg: launch app container in foreground (using entrypoint)
    shell [\$args]: open root shell inside \$APP_CONTAINER
    usershell [\$args]: open shell inside container as \$APP_USER
    build [\$args]: rebuild app containers ($BUILD_CONTAINERS)
    yamldump [\$file]: dump yaml file with anchors resolved

    defaults:
        \$BUILD_CONTAINERS: $BUILD_CONTAINERS
        \$APP_CONTAINER: $APP_CONTAINER
        \$APP_USER: $APP_USER
    "
}

do_init() {
    for d in  $( \
        find $DIST_FILES_FOLDERS -mindepth 1 -maxdepth 1 -name "*.dist" -type f )
    do
        i="$(dirname $d)/$(basename $d .dist)"
        if [ ! -e $i ];then
            cp -fv "$d" "$i"
        else
            if ! ( diff -Nu "$d" "$i" );then
                echo "Press enter to continue";read -t 120
            fi
        fi
        $EDITOR $i
    done
}

do_python() {
    do_usershell ../venv/bin/python $@
}

do_manage() {
    do_python manage.py $@
}

do_yamldump() {
    local bargs=$@
    if [ -e local/corpusops.bootstrap/venv/bin/activate ];then
        . local/corpusops.bootstrap/venv/bin/activate
    fi
    set -- .ansible/scripts/yamldump.py
    $@ $bargs
}

do_main() {
    local args=${@:-usage}
    local actions="@(shell|usage|usershell|usage|install_docker|setup_corpusops"
    actions="$actions|coverage|linting|manage|python|yamldump"
    actions="$actions|init|up|fg|pull|build|runserver|down|run_server|tests|test)"
    action=${1-}
    if [[ -n $@ ]];then shift;fi
    set_dc
    case $action in
        $actions) do_$action $@;;
        *) do_usage;;
    esac
}
cd "$W"
do_main "$@"
