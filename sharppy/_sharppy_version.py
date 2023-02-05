#!/usr/bin/env python
import os.path
import subprocess
release = True
__version__ = '1.4.1'
__version_name__ = 'Jellison'
__upstream_version__ = '1.4.0'
__upstream_version_name__ = "Andover"
__brand__ = 'SHARPpy IMET'

_repository_path = os.path.split(__file__)[0]
_git_file_path = os.path.join(_repository_path, '__git_version__.py')


def _minimal_ext_cmd(cmd):
    # construct minimal environment
    env = {}
    for k in ['SYSTEMROOT', 'PATH']:
        v = os.environ.get(k)
        if v is not None:
            env[k] = v
    # LANGUAGE is used on win32
    env['LANGUAGE'] = 'C'
    env['LANG'] = 'C'
    env['LC_ALL'] = 'C'
    out = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                           env=env).communicate()[0]
    return out

def get_git_branch():
    '''
    Gets the current Git branch.

    '''
    try:
        out = _minimal_ext_cmd(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
        branch = out.strip().decode('ascii')
    except:
        branch = ''
    return branch


def get_git_hash():
    '''
    Gets the last GIT commit hash and date for the repository, using the
    path to this file.

    '''
    try:
        out = _minimal_ext_cmd(['git', 'rev-parse', '--short', 'HEAD'])
        revision = out.strip().decode('ascii')
    except:
        revision = ''
    return revision


def get_git_date(git_hash):
    '''
    Gets the date of the last commit.

    '''
    try:
        out = _minimal_ext_cmd(['git', 'show', git_hash, '--date=short',
                                '--format="%ad"'])
        date = out.strip().decode('ascii').split('"')[1]
    except:
        date = ''
    return date


def get_git_revision():
    git_branch = get_git_branch()
    git_hash = get_git_hash()
    git_date = get_git_date(git_hash)

    if git_branch:
        rev = '.dev0+%s-%s(%s)' % (git_branch, git_hash, git_date)
    else:
        rev = ''
    return rev


def write_git_version():
    '''
    Write the GIT revision to a file.

    '''
    rev = get_git_revision()
    if rev == "":
        if os.path.isfile(_git_file_path):
            return
    gitfile = open(_git_file_path, 'w')
    gitfile.write('rev = "%s"\n' % rev)
    gitfile.close()


def get_version():
    '''
    Get the version of the package, including the GIT revision if this
    is an actual release.

    '''
    version = __version__
    if not release:
        try:
            from . import __git_version__
            version += __git_version__.rev
        except ImportError:
            version += get_git_revision()
    return version





if __name__ == "__main__":
    write_git_version()
