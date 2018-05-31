#!/usr/bin/env python3

import sys
import os
import getopt
import shutil
import json
import urllib.request
import hashlib
import tarfile
import re

exe_name = 'docker-bundle'
project_name = 'Docker-bundle'
bundle_install_dir = 'docker'
bundles_dir = 'bundles'
version_code = '0.1.0'
version_number = 1

#------------------------------------------------------------------------

config_path = os.path.expanduser(os.path.join('~', '.' + exe_name))
file_source_list = 'sources.list'
file_config = 'config.json'
source_list_file_path = os.path.join(config_path, file_source_list)
config_file_path = os.path.join(config_path, file_config)
packages_dir = 'packages'
default_source = 'https://docker-bundle.github.io/bundles.json'
upgrade_info_url = 'https://docker-bundle.github.io/update.json'

config = {
    # <version_number>: skip a version update
    # 'all': don't update
    'skip_version_number': '',
    'upgrade_info_url': upgrade_info_url,
}

def write_config(config):
    f = open(config_file_path, 'w')
    f.write(json.dumps(config, indent=2))
    f.flush()
    f.close()

def init_config_file():
    try:
        os.makedirs(config_path)
    except:
        pass
    try:
        if not os.path.isfile(source_list_file_path):
            sources_list = open(source_list_file_path, 'w')
            sources_list.write(default_source)
            sources_list.flush()
            sources_list.close()
    except:
        print('[WARNING] Load sources list failed.')
    try:
        if not os.path.isfile(config_file_path):
            write_config(config)
        else:
            config.update(json.loads(open(config_file_path).read()))
    except:
        print('[WARNING] Load config file failed.')

#------------------------------------------------------------------------

def upgrade(user_call_update = False, update_with_ask = True):
    skip_version_number = config['skip_version_number']
    if not user_call_update and skip_version_number.lower() == 'all':
        return

    update_info = {
        # must have
        'url': '',
        'hash': '',
        'version_code': version_code,
        'version_number': version_number,

        # option

        # ask: ask for update
        # silent: silent update
        'mode': 'normal',
    }
    try:
        update_info.update(json.loads(urllib.request.urlopen(config['upgrade_info_url']).read()))
    except:
        return

    update_url = update_info['url']
    update_hash = update_info['hash']
    update_version_code = update_info['version_code']
    update_version_number = update_info['version_number']
    update_mode = update_info['mode'].lower()

    if '' == update_url or '' == update_hash or '' == update_version_code:
        return

    if int(update_version_number) <= version_number:
        if user_call_update:
            print('-'*80)
            print('     %s is newest version.'%exe_name)
            print('-'*80)
        return

    is_ask_for_upgrade = update_mode == 'ask'
    is_silent_upgrade = update_mode == 'silent'

    if not user_call_update and not is_silent_upgrade\
        and not is_ask_for_upgrade\
        and skip_version_number >= str(update_version_number):
        return

    if not is_silent_upgrade and (is_ask_for_upgrade or update_with_ask):
        answer = input(
"""--------------------------------------------------------------------------------
    A newly version (%s) of %s is available. Upgrade?
            [Y]= Yes
            [N]= Not now
            [S]= Skip this version
            [D]= Disable upgrade
--------------------------------------------------------------------------------
    Answer: [Y]: """%(update_version_code,exe_name))[:1].upper()
        print()

        if answer == 'N':
            return
        elif answer == 'D':
            config['skip_version_number'] = 'all'
            write_config(config)
            return
        elif answer == 'S':
            config['skip_version_number'] = str(update_version_number)
            write_config(config)
            return
    try:
        new_exe = urllib.request.urlopen(update_url).read()

        if md5(new_exe) != update_hash:
            if user_call_update or is_ask_for_upgrade:
                print('[FAILED]         Upgrade data hash error!')
            return

        f = open(__file__,'wb')
        f.write(new_exe)
        f.flush()
        f.close()
        if user_call_update or is_ask_for_upgrade:
            print('='*80)
            print('         %s (%s) is up to date in your next command.'%(project_name, update_version_code))
            print('='*80)
    except:
        if user_call_update or is_ask_for_upgrade:
            print('[FAILED]         upgrade:',sys.exc_info()[1])
            return

#------------------------------------------------------------------------

is_installed = False

# import bundle.py
def load_sub_bundle():
    current_path = os.getcwd()
    paths = []
    while True:
        paths.append(os.path.join(current_path, bundle_install_dir))
        parent_path = os.path.dirname(current_path)
        if parent_path == current_path:
            break
        current_path = parent_path
    bak_path = sys.path
    sys.path = paths
    bundles = {}
    try:
        import bundle
        os.chdir(os.path.dirname(bundle.__file__))
        bundles.update(bundle.load_bundles())
        global is_installed
        is_installed = True
    except ImportError:
        pass
    sys.path = bak_path
    return bundles

# import from '__file__/bundles_dir'
def load_bundles(bundle_dir_path = os.path.join(os.path.dirname(__file__), bundles_dir)):
    bundles = {}
    try:
        bundle_names = list(map(lambda x:x[0:-3], filter(lambda x:x[-3:]=='.py', os.listdir(bundle_dir_path))))
    except:
        bundle_names = []
    if len(bundle_names) > 0:
        sys.path.insert(0, bundle_dir_path)
        for bundle in bundle_names:
            module = __import__(bundle)
            if 'actions' in dir(module):
                bundles.update(__import__(bundle).actions)
    return bundles

#------------------------------------------------------------------------

def load_source():
    return set(filter(lambda x:x!='', map(lambda x:x.strip(), open(source_list_file_path).readlines())))

def write_source(sources):
    f = open(source_list_file_path, 'w')
    for source in sources:
        f.write(source + '\n')
    f.flush()
    f.close()


def load_packages(sources = []):
    try:
        sources += load_source()
    except:
        pass
    if len(sources) == 0:
        sources = [default_source]

    packages = {}
    for source in sources:
        try:
            packages.update(json.loads(urllib.request.urlopen(source).read()))
        except:
            pass
    return packages

#------------------------------------------------------------------------
# install

def md5(data):
    if type(data) == str:
        data = data.encode()
    return hashlib.md5(data).hexdigest()

def install_from_dir(package_path, target_path):
    try:
        shutil.copytree(package_path, target_path, ignore=shutil.ignore_patterns('.git'))
        return True
    except:
        print('[ERROR]      Install from dir \'%s\' failed, %s.'%package_path, sys.exc_info()[1])
        return None

def install_from_tarfile(package_path, target_path):
    try:
        t = tarfile.open(package_path, "r:gz")
        t.extractall(target_path)
        return True
    except:
        print('[ERROR]      Package illegal.')
        return None

def install_from_url(package_name, package_path, target_path):
    file_name = package_name + '-' + md5(package_path) + '.bundle'
    download_dir = os.path.join(config_path, packages_dir)
    download_path = os.path.join(download_dir, file_name)
    try:
        os.makedirs(download_dir)
    except:
        pass
    if os.path.isfile(download_path):
        print('[INFO]       Load from cache...')
        return install_from_tarfile(download_path, target_path)
    try:
        urllib.request.urlretrieve(package_path, download_path)
        return install_from_tarfile(download_path, target_path)
    except:
        print('[ERROR]      Download \'%s\' failed, %s.'%package_path, sys.exc_info()[1])
    return None

def install_from_git(package_name, package_path, target_path, branch = 'master'):
    file_name = package_name + '-' + md5(package_path) + '.bundle'
    download_dir = os.path.join(config_path, packages_dir)
    download_path = os.path.join(download_dir, file_name)
    success = False
    if os.path.isdir(download_path):
        if 0 == os.system('cd "%s" && git checkout %s && git pull -f'%(download_path, branch)):
            success = True
        else:
            try:
                shutil.rmtree(download_path)
            except:
                pass
    if not success and not os.path.isdir(download_path):
        if 0 == os.system("git clone --depth 1 \"%s\" \"%s\" -b %s"%(package_path, download_path, branch)):
            success = True

    if not success:
        print('[ERROR]      Pull \'%s\' failed.'%package_path)
        return None

    return install_from_dir(download_path, target_path)

def install_from_package(package_name, package_path, target_path):
    if package_path.find('http://') == 0 or package_path.find('https://') == 0:
        return install_from_url(package_name, package_path, target_path)
    elif os.path.isdir(package_path):
        return install_from_dir(package_path, target_path)
    elif os.path.isfile(package_path):
        return install_from_tarfile(package_path, target_path)
    else:
        print('[ERROR]      Can\'t find package \'%s\' in \'%s\''%(package_name, package_path))
        return None

def install(argv = []):
    def install_help():
        print(
"""
Usage:
    %(name)s install [option] <bundle-name>

Options:
    -p, --package                           Install bundle from package or dir, not from source.
    -s, --source <source>                   Find bundle from given source.

Description:
    <bundle-name>                           Run '%(name)s search <your bundle>' get bundle-names, or in '-p' for package path.
"""%{'name': exe_name})

    opts, args = getopt.getopt(argv, 'ps:', ['package', 'source='])

    if len(args) == 0:
        install_help()
        return

    target_path = os.path.join(os.getcwd(), bundle_install_dir)

    if is_installed or os.path.isdir(target_path):
        print('         %(project_name)s already installed, if want reinstall, manully delete \'docker\' folder first.'%{'project_name': project_name})
        return

    bundle_name = args[0]

    use_sources = []
    from_package = False
    for opt in opts:
        if opt[0] == '-p' or opt[0] == '--package':
            from_package = True
        elif opt[0] == '-s' or opt[0] == '--source':
            use_sources.append(opt[1])

    result = None

    if from_package:
        result = install_from_package(bundle_name, bundle_name, target_path)
    else:
        print('[INFO]       Fetching source list...')
        upgrade()
        packages = load_packages(use_sources)

        if bundle_name not in packages:
            print("[ERROR]      Bundle '%s' not found."%(bundle_name))
            return

        print('[INFO]       Bundle: ' + bundle_name)

        package_info = packages[bundle_name]
        package_type = package_info.get('type')
        package_url = package_info.get('url')

        print('[INFO]       Package: ' + package_url)

        if package_type == 'git':
            result = install_from_git(bundle_name, package_url, target_path, package_info.get('branch', 'master'))
        elif not package_type:
            result = install_from_package(bundle_name, package_url, target_path)

    if not result:
        print('[ERROR]      Install bundle failed..')
        return

    # copy self to target
    self_path = os.path.join(os.path.realpath(__file__))
    shutil.copyfile(self_path, os.path.join(target_path, 'bundle.py'))
    os.chdir(target_path)

    print('[OK]         Install bundle success.')

    loaded_actions = load_bundles(os.path.join(target_path, bundles_dir))
    print('You get new Bundle Commands:')
    for name, action in loaded_actions.items():
        print("    %-30s%s"%(name, action['desc']))
    print()

#------------------------------------------------------------------------
# search

def search(argv = []):
    def search_help():
        print(
"""
Usage:
    %(name)s search <keyword>

Options:
    -n, --name                           Search in bundle-name only, not description
    -r, --regex                          Keyword use Regex
    -s, --source <source>                Find bundle from given source.
    -h, --help                           Show this.
"""%{'name': exe_name})
    opts, args = getopt.getopt(argv, 'nrs:h', ['name', 'regex', 'source=', 'help'])

    if len(args) == 0:
        search_help()
        return

    keyword = args[0]

    use_sources = []
    name_only = False
    use_regex = False
    for opt in opts:
        if opt[0] == '-n' or opt[0] == '--name':
            name_only = True
        elif opt[0] == '-r' or opt[0] == '--regex':
            use_regex = True
        elif opt[0] == '-s' or opt[0] == '--source':
            use_sources.append(opt[1])
        elif opt[0] == '-h' or opt[0] == '--help':
            search_help()
            exit()

    upgrade()
    packages = load_packages(use_sources)
    if use_regex:
        re_keyword = re.compile(keyword)

    def check(content):
        if use_regex:
            return re_keyword.search(content) != None
        else:
            return content.find(keyword) >=0

    print("%-40s%s"%('NAME', 'Description'))
    for name, info in packages.items():
        desc = ''
        if 'desc' in info:
            desc = info['desc']
        if check(name) or not name_only and check(desc):
            print("%-40s%s"%(name, desc))



#------------------------------------------------------------------------
# source

def source(argv = []):
    def source_help():
        print(
"""
Usage:
    %(name)s source [OPTIONS]

Options:
    -a, --add <source>                   Add Source
    -r, --remove <source>                Remove Source
    -l, --list                           List sources.
    -h, --help                           Show this.
"""%{'name': exe_name})
    opts, args = getopt.getopt(argv, 'a:r:lh', ['add=', 'remove=', 'list', 'help'])

    if len(opts) == 0:
        source_help()
        return

    sources = load_source()

    modify = False
    for opt in opts:
        if opt[0] == '-l' or opt[0] == '--list':
            for source in sources:
                print(source)
        elif opt[0] == '-h' or opt[0] == '--help':
            source_help()
            exit()
        elif opt[0] == '-a' or opt[0] == '--add':
            modify = True
            sources.add(opt[1])
        elif opt[0] == '-r' or opt[0] == '--remove':
            modify = True
            sources.remove(opt[1])
    if modify:
        write_source(sources)

# import finish
#------------------------------------------------------------------------

def help(args = []):
    print(
"""
    %(project_name)s

Usage:
    %(name)s [options] [COMMAND] [ARGS...]

Options:
    -h|--help
    -v|--version
    -e|--environment <ENV>                  Set environment variables to commands
       --check-upgrade                      Check self upgrade before action
       --upgrade                            Do self upgrade directly (without ask) if upgrade available

Commands:"""%{'name': exe_name, 'project_name': project_name})
    for name, action in base_actions.items():
        print("    %-30s%s"%(name, action['desc']))
    print()
    init_actions_bundles()
    if len(bundles) > 0:
        print("Bundle Commands:")
        for name, action in bundles.items():
            print("    %-30s%s"%(name, action['desc']))
        print()
    exit()

def version(args = []):
    f = open(__file__)
    file_hash = md5(f.read())
    f.close()
    version_info = {
        'version_code': version_code,
        'version_number': version_number,
        'hash': file_hash,
    }
    print(json.dumps(version_info, indent=2))
    exit()

def environment(args = []):
    for arg in args:
        a = arg.split('=')
        a.append(a[0])
        k,v = a[:2]
        os.environ[k] = v

def action_upgrade(args = []):
    upgrade(True)
    exit()


def action_upgrade_directly(args = []):
    upgrade(True, False)
    exit()

#------------------------------------------------------------------------

# command call actions

base_actions = {
        'install': {
            'desc': 'Install bundle here',
            'action': install
            },
        'search': {
            'desc': 'Search for bundle you want',
            'action': search
            },
        'source': {
            'desc': 'Manage sources',
            'action': source
            },
        }

actions = {}

bundles = {}

def init_actions_bundles():
    actions.update(base_actions.copy())

    bundles.update(load_sub_bundle())

    bundles.update(load_bundles())

    actions.update(bundles)


#------------------------------------------------------------------------

def main():
    init_config_file()

    options = {
        '-h': help,
        '--help': help,
        '-v': version,
        '--version': version,
        '-e': environment,
        '--environment': environment,
        '--check-upgrade': action_upgrade,
        '--upgrade': action_upgrade_directly,
    }

    opts, args = getopt.getopt(sys.argv[1:], 'hve:', ['help', 'version', 'environment=', 'check-upgrade', 'upgrade'])

    for opt in opts:
        options[opt[0]]([opt[1]])

    if len(args) == 0:
        help()
        return

    init_actions_bundles()

    action = args[0]

    if action not in actions:
        print("%s: command '%s' not found."%(exe_name, action))
        return
    try:
        actions[action]['action'](args[1:])
    except getopt.GetoptError:
        print('       %s:'%action, sys.exc_info()[1])

if __name__=='__main__':
    try:
        exit(main())
    except KeyboardInterrupt:
        pass
    except getopt.GetoptError:
        print(exe_name, ':',sys.exc_info()[1])

