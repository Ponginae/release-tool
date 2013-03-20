from paver.easy import task, no_help, consume_args, call_task, needs
from os import getcwd
from sys import stdout
from git.cmd import Git
from git.repo import Repo
from git.objects.util import Actor
from getpass import getpass
from datetime import datetime

import json
import sha

tool_name = 'Release Tool'
tool_command = "release-tool"
branches = [
    'master',
    'dev',
    'qa',
    'prod'
]


@task
@no_help
@needs(['load_releaserc'])
def init_branches(options, error, info, debug):
    path = getcwd()
    git = Git(path)
    create = options.release_tool_settings['branches']

    for branch in create:
        debug('creating branch "%s"...' % branch)
        debug(git.branch(branch))

    info('Created branches ' + ', '.join(create))


@task
@no_help
def init_releaserc(debug, info):
    path = getcwd()
    git = Git(path)
    another_env = 'y'
    n_th = 'first'
    branches = []
    secrets = {}
    commands = {
        "test": "/usr/bin/true"
    }

    # get branch names and passwords
    info('\nLet\'s setup your roll process.')
    info('-------------------------------')
    while another_env.lower() == 'y' or another_env.lower() == '':
        env_name = raw_input('What\'s the name of the ' + n_th + ' environment? ')
        branches.append(env_name)
        password_required = raw_input('Should a password be required to roll here? (y/N) ')
        password = None

        if password_required.lower() == 'y':
            password = sha.new(getpass()).hexdigest()

        secrets[env_name] = password
        another_env = raw_input('Is there another environment? (Y/n) ')

        n_th = 'next'
        info('')

    info('Your roll process is:\nmaster -> ' + ' -> '.join(branches))
    info('')
    info('')

    fd = open('.releaserc', 'w')

    json.dump({
        "branches": branches,
        "commands": commands,
        "secrets": secrets
    }, fd, indent=4, separators=(',', ': '))

    debug('adding .releaserc...')
    debug(git.add('.releaserc'))


@task
@no_help
def init_remotes():
    path = getcwd()
    git = Git(path)

    has_upstream = raw_input('Is this a fork? (y/N) ')
    if has_upstream.lower() == 'y':
        upstream = raw_input('What is the url of the upstream project? ')
        git.remote('add', 'upstream', upstream)


@task
@no_help
def welcome_package(debug, info):
    path = getcwd()
    git = Git(path)

    fd = open('welcome.txt', 'w')

    fd.write('''
Welcome to {tool_name}
=======================

This tool is a helper to be used along side git.

    $ {tool_command} init # you just ran this!

    $ {tool_command} update

    $ {tool_command} roll to dev
    $ {tool_command} roll qa to prod
'''.format(tool_name=tool_name, tool_command=tool_command))

    debug('adding welcome.txt...')
    debug(git.add('welcome.txt'))

    info('Welcome to {tool_name}'.format(tool_name=tool_name))


@task
@no_help
def load_releaserc(options, error):
    try:
        releaserc = open('.releaserc')
    except IOError, e:
        error(e)
    else:
        options.release_tool_settings = json.load(releaserc)
    finally:
        releaserc.close()


@task
@consume_args
def commit(options, debug, info):
    path = getcwd()
    git = Git(path)

    debug(git.commit('-m', message(options['m'], 'commit')))

    info('Committed with message "{message}".'.format(message=options['m']))


def update_from_remote(debug, info, repo, remote_name):
    try:
        remote = repo.remote(remote_name)
    except ValueError:
        debug('no remote named "' + remote_name + '"...')
    else:
        debug('remote "' + remote_name + '" exists...')
        remote.pull(rebase=True)
        info('Updated from remote "{remote_name}"'.format(remote_name=remote_name))


@task
def update(options, error, debug, info):
    path = getcwd()
    repo = Repo(path)

    if not repo.is_dirty():
        update_from_remote(debug, info, repo, 'origin')
        update_from_remote(debug, info, repo, 'upstream')
    else:
        error('Please commit or stash your changes before continuing.')


def has_permission(if_matches):
    password = getpass()
    hash = sha.new(password)
    return if_matches == hash.hexdigest()


def message(base, type_of):
    return '''{base}

*****
This was an automated {type_of} created by {tool_name}
'''.format(base=base, type_of=type_of, tool_name=tool_name)


@task
@consume_args
@needs(['load_releaserc'])
def roll(options, debug, info, error):
    to_arg = options.args.index('to')
    path = getcwd()
    git = Git(path)
    repo = Repo(path)

    dest = None
    source = None
    active = repo.active_branch
    settings = options.release_tool_settings

    if to_arg == 0:
        source = active
        dest = options.args[1]

        #update()
    elif to_arg == 1:
        source = options.args[0]
        dest = options.args[2]
    else:
        return

    secret = settings['secrets'][str(dest)]

    if secret:
        info('Special permission is required to roll to this branch.')

    if not secret or has_permission(if_matches=secret):
        debug('rebasing {source} onto {dest}...'.format(
            source=source,
            dest=dest
        ))

        if secret:
            debug(git.rebase(source, dest))
            git.tag('-m', message('Roll from {source} to {dest} with special \
permission by {name} <{email}>.'.format(
                    source=source,
                    dest=dest,
                    name=Actor.author().name,
                    email=Actor.author().email
                ), 'tag'),
                '-s',
                'roll-from-' +
                    source + '-to-' +
                    dest + '-' +
                    datetime.utcnow().isoformat().replace(':', '.'),
                output_stream=stdout)
        else:
            debug(git.rebase(source, dest))

        debug('checking out {source}...'.format(source=source))
        debug(git.checkout(active))

        info('Rolled {source} to {dest}.'.format(source=source, dest=dest))
    else:
        error('You do not have permission to roll to this branch')


@task
def init(error, info, debug):
    path = getcwd()
    git = Git(path)

    debug('running git init...')
    debug(git.init())

    welcome_package()
    init_releaserc()

    call_task('commit', options={
        'm': 'Intializing repository'
    })

    init_branches()

    debug('')

    info('Git repository created successfully.')
