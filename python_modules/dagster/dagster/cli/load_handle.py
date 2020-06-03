import os

import six
from click import UsageError

from dagster import check
from dagster.core.definitions.reconstructable import (
    ReconstructablePipeline,
    ReconstructableRepository,
)
from dagster.utils import DEFAULT_REPOSITORY_YAML_FILENAME, all_none


def _cli_load_invariant(condition, msg=None):
    msg = (
        msg
        or 'Invalid set of CLI arguments for loading repository/pipeline. See --help for details.'
    )
    if not condition:
        raise UsageError(msg)


def recon_pipeline_for_cli_args(kwargs):
    '''Builds a ReconstructablePipeline for CLI arguments, which can be
    any of the combinations for repo/pipeline loading above.
    '''
    check.dict_param(kwargs, 'kwargs')

    pipeline_name = kwargs.get('pipeline_name')

    if pipeline_name and not isinstance(pipeline_name, six.string_types):
        if len(pipeline_name) == 1:
            pipeline_name = pipeline_name[0]
        else:
            check.failed(
                'Can only handle zero or one pipeline args. Got {pipeline_name}'.format(
                    pipeline_name=repr(pipeline_name)
                )
            )

    # Pipeline from repository YAML and pipeline_name
    if (
        pipeline_name
        and kwargs.get('module_name') is None
        and kwargs.get('python_file') is None
        and kwargs.get('repository_yaml') is not None
    ):
        _cli_load_invariant(kwargs.get('fn_name') is None)
        repo_yaml = (
            os.path.abspath(kwargs.get('repository_yaml'))
            if kwargs.get('repository_yaml')
            else DEFAULT_REPOSITORY_YAML_FILENAME
        )
        _cli_load_invariant(
            os.path.exists(repo_yaml),
            'Expected to use file "{}" to load repository but it does not exist. '
            'Verify your current working directory or CLI arguments.'.format(repo_yaml),
        )
        return ReconstructableRepository.from_legacy_repository_yaml(
            repo_yaml
        ).get_reconstructable_pipeline(pipeline_name)

    # Pipeline from repository python file
    elif kwargs.get('python_file') and kwargs.get('fn_name') and pipeline_name:
        _cli_load_invariant(kwargs.get('repository_yaml') is None)
        _cli_load_invariant(kwargs.get('module_name') is None)
        return ReconstructableRepository.for_file(
            os.path.abspath(kwargs['python_file']), kwargs['fn_name']
        ).get_reconstructable_pipeline(pipeline_name)

    # Pipeline from repository module
    elif kwargs.get('module_name') and kwargs.get('fn_name') and pipeline_name:
        _cli_load_invariant(kwargs.get('repository_yaml') is None)
        _cli_load_invariant(kwargs.get('python_file') is None)
        return ReconstructableRepository.for_module(
            kwargs['module_name'], kwargs['fn_name']
        ).get_reconstructable_pipeline(pipeline_name)

    # Pipeline from pipeline python file
    elif kwargs.get('python_file') and kwargs.get('fn_name') and not pipeline_name:
        _cli_load_invariant(kwargs.get('repository_yaml') is None)
        _cli_load_invariant(kwargs.get('module_name') is None)
        return ReconstructablePipeline.for_file(
            os.path.abspath(kwargs['python_file']), kwargs['fn_name']
        )

    # Pipeline from pipeline module
    elif kwargs.get('module_name') and kwargs.get('fn_name') and not pipeline_name:
        _cli_load_invariant(kwargs.get('repository_yaml') is None)
        _cli_load_invariant(kwargs.get('python_file') is None)
        return ReconstructablePipeline.for_module(kwargs['module_name'], kwargs['fn_name'])
    else:
        _cli_load_invariant(False)


def recon_repo_for_cli_args(kwargs):
    '''Builds a ReconstructableRepository for CLI arguments, which can be any of the combinations
    for repo loading above.
    '''
    check.dict_param(kwargs, 'kwargs')
    _cli_load_invariant(kwargs.get('pipeline_name') is None)

    if kwargs.get('workspace'):
        check.not_implemented('Workspace not supported yet in this cli command')

    if kwargs.get('repository_yaml') or all_none(kwargs):
        _cli_load_invariant(kwargs.get('module_name') is None)
        _cli_load_invariant(kwargs.get('python_file') is None)
        _cli_load_invariant(kwargs.get('fn_name') is None)
        repo_yaml = (
            os.path.abspath(kwargs.get('repository_yaml'))
            if kwargs.get('repository_yaml')
            else DEFAULT_REPOSITORY_YAML_FILENAME
        )
        _cli_load_invariant(
            os.path.exists(repo_yaml),
            'Expected to use file "{}" to load repository but it does not exist. '
            'Verify your current working directory or CLI arguments.'.format(repo_yaml),
        )
        return ReconstructableRepository.from_legacy_repository_yaml(repo_yaml)
    elif kwargs.get('module_name') and kwargs.get('fn_name'):
        _cli_load_invariant(kwargs.get('repository_yaml') is None)
        _cli_load_invariant(kwargs.get('python_file') is None)
        return ReconstructableRepository.for_module(kwargs['module_name'], kwargs['fn_name'])

    elif kwargs.get('python_file') and kwargs.get('fn_name'):
        _cli_load_invariant(kwargs.get('repository_yaml') is None)
        _cli_load_invariant(kwargs.get('module_name') is None)
        return ReconstructableRepository.for_file(
            os.path.abspath(kwargs['python_file']), kwargs['fn_name']
        )
    else:
        _cli_load_invariant(False)
