#!/usr/bin/env bash
W="$(cd $(dirname $(readlink -f "$0"))/ && pwd)"
vv() { echo "$@">&2;"$@"; }
dvv() { if [[ -n "${DEBUG-}" ]];then echo "$@">&2;fi;"$@"; }
reset
out2="$( cd "$W/.." && pwd)"
out="$(dirname $out2)/$(basename $out2)_pre"
venv=${venv:-$HOME/tools/cookiecutter/activate}
if [ -e "$venv/bin/activate" ];then . "$venv/bin/activate";fi
set -e
u=${COOKIECUTTER-${1-}}
if [[ -z "$u" ]];then
    u="$HOME/.cookiecutters/cookiecutter-terra{{cookiecutter.app_suffix}}"
    if [ ! -e "$u" ];then
        u="https://github.com/makinacorpus/$(basename $u).git"
    else
        cd "$u"
        git fetch origin
        git pull --rebase
    fi
fi
if [ -e "$out" ];then vv rm -rf "$out";fi
vv cookiecutter --no-input -o "$out" -f "$u" \
        tld_domain="{{cookiecutter.tld_domain}}" \
        name="{{cookiecutter.name}}" \
        git_ns="{{cookiecutter.git_ns}}"  \
        dev_port="{{cookiecutter.dev_port}}" \
        staging_port="{{cookiecutter.staging_port}}" \
        qa_port="{{cookiecutter.qa_port}}" \
        prod_port="{{cookiecutter.prod_port}}"
# sync the gen in a second folder for intermediate regenerations
dvv rsync -aA \
    --include "local/terra-*" \
    --exclude "local/*" --exclude lib \
    $( if [ -e ${out2}/.git ];then echo "--exclude .git";fi; ) \
    "$out/" "${out2}/"
dvv cp -f "$out/local/regen.sh" "$out2/local"
if [[ -z ${NO_RM-} ]];then dvv rm -rf "${out}";fi
echo "Your project is generated in: $out2" >&2
echo "Please note that you can generate with the local/regen.sh file" >&2
# vim:set et sts=4 ts=4 tw=80:
