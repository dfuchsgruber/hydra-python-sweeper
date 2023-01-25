# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved
from pytest import mark

from hydra.core.plugins import Plugins
from hydra.plugins.sweeper import Sweeper
from hydra.test_utils.launcher_common_tests import (
    BatchedSweeperTestSuite,
    IntegrationTestSuite,
    LauncherTestSuite,
)
from hydra.test_utils.test_utils import TSweepRunner

from hydra_plugins.python_sweeper_plugin.python_sweeper import PythonSweeper

def test_multiple_entrypoints(hydra_sweep_runner: TSweepRunner) -> None:
    sweep = hydra_sweep_runner(
        calling_file=__file__,
        calling_module=None,
        config_path="configs",
        config_name="overrides.yaml",
        task_function=None,
        overrides=["hydra/sweeper=python", "hydra/launcher=basic", "hydra.sweeper.entrypoints=[configs.overrides.configure_cli_overrides_python, configs.overrides.configure_2]", "foo=1,2"],
    )
    with sweep:
        assert sweep.returns is not None
        job_ret = sweep.returns[0]
        assert len(job_ret) == 8
        assert job_ret[0].overrides == ["foo=1", "+bar=0", "+bizz=1"]
        assert job_ret[0].cfg == {"foo": 1, "bar": 0, "bizz" : 1}
        
        assert job_ret[1].overrides == ["foo=1", "+bar=0", "+bizz=11"]
        assert job_ret[1].cfg == {"foo": 1, "bar": 0, "bizz" : 11}
        
        assert job_ret[2].overrides == ["foo=1", "+bar=1", "+bizz=1"]
        assert job_ret[2].cfg == {"foo": 1, "bar": 1, "bizz" : 1}
        
        assert job_ret[3].overrides == ["foo=1", "+bar=1", "+bizz=11"]
        assert job_ret[3].cfg == {"foo": 1, "bar": 1, "bizz" : 11}
        
        assert job_ret[4].overrides == ["foo=2", "+bar=0", "+bizz=1"]
        assert job_ret[4].cfg == {"foo": 2, "bar": 0, "bizz" : 1}
        
        assert job_ret[5].overrides == ["foo=2", "+bar=0", "+bizz=11"]
        assert job_ret[5].cfg == {"foo": 2, "bar": 0, "bizz" : 11}
        
        assert job_ret[6].overrides == ["foo=2", "+bar=1", "+bizz=1"]
        assert job_ret[6].cfg == {"foo": 2, "bar": 1, "bizz" : 1}
        
        assert job_ret[7].overrides == ["foo=2", "+bar=1", "+bizz=11"]
        assert job_ret[7].cfg == {"foo": 2, "bar": 1, "bizz" : 11}
    
def test_discovery() -> None:
    # Tests that this plugin can be discovered via the plugins subsystem when looking at the Sweeper plugins
    assert PythonSweeper.__name__ in [
        x.__name__ for x in Plugins.instance().discover(Sweeper)
    ]


def test_launched_jobs(hydra_sweep_runner: TSweepRunner) -> None:
    sweep = hydra_sweep_runner(
        calling_file=None,
        calling_module="hydra.test_utils.a_module",
        config_path="configs",
        config_name="compose.yaml",
        task_function=None,
        overrides=["hydra/sweeper=python", "hydra/launcher=basic", "foo=1,2"],
    )
    with sweep:
        assert sweep.returns is not None
        job_ret = sweep.returns[0]
        assert len(job_ret) == 2
        assert job_ret[0].overrides == ["foo=1"]
        assert job_ret[0].cfg == {"foo": 1, "bar": 100}
        assert job_ret[1].overrides == ["foo=2"]
        assert job_ret[1].cfg == {"foo": 2, "bar": 100}


def test_cli_overrides_python(hydra_sweep_runner: TSweepRunner) -> None:
    sweep = hydra_sweep_runner(
        calling_file=__file__,
        calling_module=None,
        config_path="configs",
        config_name="overrides.yaml",
        task_function=None,
        overrides=["hydra/sweeper=python", "hydra/launcher=basic", "hydra.sweeper.entrypoints=[configs.overrides.configure_cli_overrides_python]", "foo=1,2"],
    )
    with sweep:
        assert sweep.returns is not None
        job_ret = sweep.returns[0]
        assert len(job_ret) == 4
        assert job_ret[0].overrides == ["foo=1", "+bar=0"]
        assert job_ret[0].cfg == {"foo": 1, "bar": 0}
        assert job_ret[1].overrides == ["foo=1", "+bar=1"]
        assert job_ret[1].cfg == {"foo": 1, "bar": 1}
        assert job_ret[2].overrides == ["foo=2", "+bar=0"]
        assert job_ret[2].cfg == {"foo": 2, "bar": 0}
        assert job_ret[3].overrides == ["foo=2", "+bar=1"]
        assert job_ret[3].cfg == {"foo": 2, "bar": 1}
        
def test_remove_duplicates(hydra_sweep_runner: TSweepRunner) -> None:
    sweep = hydra_sweep_runner(
        calling_file=__file__,
        calling_module=None,
        config_path="configs",
        config_name="overrides.yaml",
        task_function=None,
        overrides=["hydra/sweeper=python", "hydra/launcher=basic", 
                   "hydra.sweeper.remove_duplicates=True", "foo=1,1", "+bar=1,1"],
    )
    with sweep:
        assert sweep.returns is not None
        job_ret = sweep.returns[0]
        assert len(job_ret) == 1
        assert job_ret[0].overrides == ["foo=1", "+bar=1"]
        assert job_ret[0].cfg == {"foo": 1, "bar": 1}
        
def test_entrypoints(hydra_sweep_runner: TSweepRunner) -> None:
    sweep = hydra_sweep_runner(
        calling_file=__file__,
        calling_module=None,
        config_path="configs",
        config_name="overrides.yaml",
        task_function=None,
        overrides=["hydra/sweeper=python", "hydra/launcher=basic",
                   "hydra.sweeper.entrypoints=[configs.overrides.configure_cli_overrides_python]"],
    )
    with sweep:
        assert sweep.returns is not None
        job_ret = sweep.returns[0]
        assert len(job_ret) == 2
        assert job_ret[0].overrides == ["foo=33", "+bar=0"]
        assert job_ret[0].cfg == {"foo": 33, "bar": 0}
        assert job_ret[1].overrides == ["foo=33", "+bar=1"]
        assert job_ret[1].cfg == {"foo": 33, "bar": 1}
        

# Run launcher test suite with the basic launcher and this sweeper
@mark.parametrize(
    "launcher_name, overrides",
    [
        (
            "basic",
            [
                # CHANGE THIS TO YOUR SWEEPER CONFIG NAME
                "hydra/sweeper=python"
            ],
        )
    ],
)
class TestPythonSweeper(LauncherTestSuite):
    ...


# Many sweepers are batching jobs in groups.
# This test suite verifies that the spawned jobs are not overstepping the directories of one another.
@mark.parametrize(
    "launcher_name, overrides",
    [
        (
            "basic",
            [
                # CHANGE THIS TO YOUR SWEEPER CONFIG NAME
                "hydra/sweeper=python",
                # This will cause the sweeper to split batches to at most 2 jobs each, which is what
                # the tests in BatchedSweeperTestSuite are expecting.
                "hydra.sweeper.max_batch_size=2",
            ],
        )
    ],
)
class TestPythonSweeperWithBatching(BatchedSweeperTestSuite):
    ...


# Run integration test suite with the basic launcher and this sweeper
@mark.parametrize(
    "task_launcher_cfg, extra_flags",
    [
        (
            {},
            [
                "-m",
                # CHANGE THIS TO YOUR SWEEPER CONFIG NAME
                "hydra/sweeper=python",
                "hydra/launcher=basic",
            ],
        )
    ],
)
class TestPythonSweeperIntegration(IntegrationTestSuite):
    pass