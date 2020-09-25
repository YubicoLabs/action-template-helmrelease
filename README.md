# action-template-helmrelease

A GitHub Action for templating one or more Flux CD HelmRelease resources. It parses the Helm chart repository, chart name, chart version, and values and passes those to `helm template` for rendering. The most common use case is to render the full resources so they can be checked with `conftest` or another static analysis tool in a later step in the CI job.

If a directory is specified for the `hr-path` option, it will be recursively searched for HelmRelease resources and each located HelmRelease will be templated. The format of the output filename is `${RELEASE_NAME}_${CHART_NAME}_${CHART_VER}.yaml`.

## Options

| Option  | Description                                | Default | Required |
|---------|--------------------------------------------|---------|----------|
| hr-path | Path to the HelmRelease file or directory  |         | yes      |
| out-dir | Path to the directory to write the outputs | .       | yes      |

## Example Usage

```yaml
name: template-helmrelease
on: [pull_request]
jobs:
  hr-template:
    runs-on: ubuntu-latest
    steps:
      - name: checkout
        uses: actions/checkout@v2
      - name: template
        uses: YubicoLabs/action-template-helmrelease@v1
        with:
          hr-path: your-helmrelease.yaml
```
