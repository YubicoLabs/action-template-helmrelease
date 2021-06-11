#!/usr/bin/env python3

from sys import argv, exit
from os import mkdir, path
import yaml
import subprocess
import pathlib


helm_releases = []
helm_repos = []


def check_args() -> None:
    if len(argv) < 3:
        print('Error! Missing arguments')
        print(f"Usage: {argv[0]} <path_to_helmrelease> <output_directory>")
        exit(1)


def get_releases(path: str) -> None:
    release_files = pathlib.Path(argv[1]).rglob('*.y*ml')
    for file in release_files:
        with open(file, 'r') as stream:
            yamls = yaml.safe_load_all(stream)
            for yaml_parsed in yamls:
                if yaml_parsed is None:
                    continue
                if 'kind' not in yaml_parsed.keys():
                    continue
                if yaml_parsed['kind'] == 'HelmRelease':
                    helm_releases.append(yaml_parsed)
                if yaml_parsed['kind'] == 'HelmRepository':
                    helm_repos.append(yaml_parsed)


def template_v1(release: dict) -> None:
    chart_spec = release['spec']['chart']
    if 'git' in chart_spec.keys():
        raise Exception('Git chart source is not currently supported')

    cfg = {
        'chart_name': chart_spec['name'],
        'chart_version': chart_spec['version'],
        'chart_repo_url': chart_spec['repository'],
        'install_name': release['metadata']['name'],
        'install_values': release['spec']['values'],
        'install_namespace': get_install_namespace_v1(release),
    }
    helm_template(cfg)


def template_v2(release: dict) -> None:
    chart_spec = release['spec']['chart']['spec']
    if 'git' in chart_spec.keys():
        raise Exception('Git chart source is not currently supported')

    cfg = {
        'chart_name': chart_spec['chart'],
        'chart_version': chart_spec['version'],
        'chart_repo_url': lookup_repo_url(chart_spec['sourceRef']['name']),
        'install_name': release['metadata']['name'],
        'install_values': release['spec']['values'],
        'install_namespace': get_install_namespace_v2(release),
    }
    helm_template(cfg)


def lookup_repo_url(name: str) -> str:
    for repo in helm_repos:
        if repo['metadata']['name'] == name:
            return repo['spec']['url']

    raise Exception(f"HelmRepository {name} not found, unable to obtain repo URL")


def get_install_namespace_v1(release: dict) -> str:
    chart_spec = release['spec']['chart']
    if 'targetNamespace' in chart_spec.keys():
        return chart_spec['targetNamespace']

    return release['metadata']['namespace']


def get_install_namespace_v2(release: dict) -> str:
    chart_spec = release['spec']['chart']['spec']
    if 'targetNamespace' in chart_spec.keys():
        return chart_spec['targetNamespace']

    return release['metadata']['namespace']


def helm_template(cfg: dict) -> None:
    out_file_name = path.join(
        f"{argv[2]}",
        (
            f"{cfg['install_namespace']}_"
            f"{cfg['install_name']}_"
            f"{cfg['chart_name']}_"
            f"{cfg['chart_version']}.yaml"
        ),
    )
    with open(out_file_name, 'w') as out_file:
        proc = subprocess.Popen([
            'helm', 'template', cfg['install_name'], cfg['chart_name'],
            '--repo', cfg['chart_repo_url'],
            '--version', str(cfg['chart_version']),
            '--namespace', cfg['install_namespace'],
            '--values', '-',
        ], stdin=subprocess.PIPE, stdout=out_file)
        proc.communicate(yaml.dump(cfg['install_values']).encode())
        return_code = proc.poll()
        if return_code != 0:
            raise Exception('helm template command failed')


if __name__ == '__main__':
    check_args()
    try:
        mkdir(argv[2])
    except FileExistsError:
        pass
    except Exception as e:
        print('Error! Unable to create output directory')
        print(e)
        exit(1)

    try:
        get_releases(argv[1])
    except Exception as e:
        print('Error while getting HelmReleases')
        print(e)
        exit(1)

    if len(helm_releases) == 0:
        print('Warning: No HelmRelease files found')
        exit(0)

    for release in helm_releases:
        try:
            api_ver = release['apiVersion']
            if api_ver.startswith('helm.toolkit.fluxcd.io'):
                template_v2(release)
            elif api_ver.startswith('helm.fluxcd.io'):
                template_v1(release)
            else:
                raise Exception(f"Unsupported API group: {api_ver.split('/')[0]}")
        except KeyError as e:
            print('Error! One of the YAMLs is missing a required value')
            print(f"Key name: {e}")
            exit(1)
        except Exception as e:
            print('Unexpected error while templating a release')
            print(e)
            exit(1)

        print(
            f"Successfully templated release {release['metadata']['name']}"
            f" for namespace {release['metadata']['namespace']}"
        )
