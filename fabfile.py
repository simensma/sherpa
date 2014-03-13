from fabric.api import env, run, cd

import fabfile_settings

env.use_ssh_config = True
env.hosts = ['sherpa_container']

# gateway data (user, identity file) isn't read from ssh_config, so we'll have to put it here
env.gateway = 'ubuntu@sherpa'
env.key_filename = fabfile_settings.GW_KEY_FILENAME

# This makes ssh substantially faster.
# See https://github.com/paramiko/paramiko/pull/192
env.disable_known_hosts = True

setenv = '. /etc/container_environment.sh && . /sherpa/env/bin/activate'

def deploy_soft():
    with cd('/sherpa'):
        # Note that we're blanking DJANGO_SETTINGS_MODULE when running django-admin.py due to the project being named the same as the root folder.
        # See http://stackoverflow.com/a/6949892/302484
        commands = ' && '.join([
            'git pull --tags github master',
            './manage.py migrate',
            'DJANGO_SETTINGS_MODULE="" django-admin.py compilemessages',
            'sv hup sherpa',
        ])
        run(setenv + ' && ' + commands)

def deploy_hard():
    with cd('/sherpa'):
        commands = ' && '.join([
            'sv stop sherpa',
            'git pull --tags github master',
            './manage.py migrate',
            'DJANGO_SETTINGS_MODULE="" django-admin.py compilemessages',
            'sv start sherpa'
        ])
        run(setenv + ' && ' + commands)
