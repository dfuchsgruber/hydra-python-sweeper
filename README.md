# Hydra Python Sweeper

Provides a sweeper for [Hydra](https://hydra.cc) that extends sweeps using a custom python entrypoint(s). This allows to define complex experiment configurations that can not be obtained as a cartesian product of individual parameter settings. Imagine for example running an experiment where you want to define a model with a variable amount of layers and number of hidden units within. Say, the number of layers should be between 1 and 3 and for each layer you want to experiment with either 32 or 64 hidden units.

Running with the standard hydra sweeper, e.g. `python train.py --config-name multilayer -m num_hidden_first=32,64 num_hidden_second=32,64, num_hidden_third=32,64, num_layers=1,2,3` creates 24 configrations, while only 14 will be needed. Instead, this plugin allows to define the sweep in pure python code.

```yaml
# config/multilayer.yaml
defaults:
    - override hydra/sweeper: python

hydra:
    sweeper:
        entrypoints: 
            - config.multilayer.configure

# other model settings
num_layers: ???
num_hidden: ???

# more configurations ...
```

```python
# config/multilayer.py
import itertools

def configure():
    sweep = []
    for num_layers in range(1, 4):
        for num_hidden in itertools.product((32, 64), repeat=num_layers):
            sweep.append({
                'num_layers' : num_layers,
                'num_hidden' : list(num_hidden),
            }.items())
    return sweep
```

This creates all neccessary and valid 14 configurations for the experiment setting.

## Installation

```sh
git clone https://github.com/WodkaRHR/hydra_python_sweeper
cd hydra_python_sweeper
pip install .
```

## Usage

### Sweeper configuration

<details>
    <summary>The sweeper has the following default parameters:</summary>

```yaml
# @package hydra.sweeper
_target_: hydra_plugins.hydra_python_sweeper.python_sweeper.PythonSweeper
max_batch_size: null
# entrypoints for python, can be null
entrypoints: []
# removes duplicate configurations
remove_duplicates: false
```
</details>

### Running experiments

Running the [example](https://github.com/WodkaRHR/hydra_python_lancher/blob/main/example/train.py) with `python example/train.py --config-name multilayer -m` launches the configured jobs.
<details>
    <summary>Experiment invocation and output</summary>

```
[2023-01-25 10:43:48,931][HYDRA] PythonSweeper(max_batch_size=None, entrypoints=['config.example.configure']) sweeping
[2023-01-25 10:43:48,934][HYDRA] Sweep output dir : multirun/2023-01-25/10-43-48
[2023-01-25 10:43:50,170][HYDRA] Launching 14 jobs locally
[2023-01-25 10:43:50,170][HYDRA]        #0 : num_layers=1 num_hidden=[32]
num_layers: 1
num_hidden:
- 32

[2023-01-25 10:43:50,343][HYDRA]        #1 : num_layers=1 num_hidden=[64]
num_layers: 1
num_hidden:
- 64

[2023-01-25 10:43:50,525][HYDRA]        #2 : num_layers=2 num_hidden=[32, 32]
num_layers: 2
num_hidden:
- 32
- 32

[2023-01-25 10:43:50,696][HYDRA]        #3 : num_layers=2 num_hidden=[32, 64]
num_layers: 2
num_hidden:
- 32
- 64

[2023-01-25 10:43:50,875][HYDRA]        #4 : num_layers=2 num_hidden=[64, 32]
num_layers: 2
num_hidden:
- 64
- 32

[2023-01-25 10:43:51,062][HYDRA]        #5 : num_layers=2 num_hidden=[64, 64]
num_layers: 2
num_hidden:
- 64
- 64

[2023-01-25 10:43:51,230][HYDRA]        #6 : num_layers=3 num_hidden=[32, 32, 32]
num_layers: 3
num_hidden:
- 32
- 32
- 32

[2023-01-25 10:43:51,423][HYDRA]        #7 : num_layers=3 num_hidden=[32, 32, 64]
num_layers: 3
num_hidden:
- 32
- 32
- 64

[2023-01-25 10:43:51,597][HYDRA]        #8 : num_layers=3 num_hidden=[32, 64, 32]
num_layers: 3
num_hidden:
- 32
- 64
- 32

[2023-01-25 10:43:51,762][HYDRA]        #9 : num_layers=3 num_hidden=[32, 64, 64]
num_layers: 3
num_hidden:
- 32
- 64
- 64

[2023-01-25 10:43:51,937][HYDRA]        #10 : num_layers=3 num_hidden=[64, 32, 32]
num_layers: 3
num_hidden:
- 64
- 32
- 32

[2023-01-25 10:43:52,105][HYDRA]        #11 : num_layers=3 num_hidden=[64, 32, 64]
num_layers: 3
num_hidden:
- 64
- 32
- 64

[2023-01-25 10:43:52,282][HYDRA]        #12 : num_layers=3 num_hidden=[64, 64, 32]
num_layers: 3
num_hidden:
- 64
- 64
- 32

[2023-01-25 10:43:52,460][HYDRA]        #13 : num_layers=3 num_hidden=[64, 64, 64]
num_layers: 3
num_hidden:
- 64
- 64
- 64
```
</details>

Each entrypoint method should take no arguments and return an `Iterable` of `Iterable` of `Tuple`s that are the key-value pairs for overriding. Each `Iterable` of `Tuple`s defines the overrides for one experiment, where the overrides are given as key-value pairs. The order of experiments will be respected when launching jobs.

### Combining with command line overrides

Furthermore, the python entrypoint sweep settings can be combined with command line overrides. To that end, the cartesian product between all command line configurations and python configurations will be launched. For example, if the command line overrides define 8 settings and the python entrypoints define 14 settings, 8 * 14 jobs will be launched.

If both the command line overrides and python overrides define the same key, the command line override will preceed. Running the [example](https://github.com/WodkaRHR/hydra_python_lancher/blob/main/example/train.py) with `python example/train.py --config-name multilayer -m +activation=relu,tanh` launches the configured jobs.

<details>
    <summary>Experiment invocation and output</summary>

```
[2023-01-25 10:53:26,289][HYDRA] PythonSweeper(max_batch_size=None, entrypoints=['config.example.configure']) sweeping
[2023-01-25 10:53:26,291][HYDRA] Sweep output dir : multirun/2023-01-25/10-53-26
[2023-01-25 10:53:28,780][HYDRA] Launching 28 jobs locally
[2023-01-25 10:53:28,780][HYDRA] 	#0 : +activation=relu num_layers=1 num_hidden=[32]
num_layers: 1
num_hidden:
- 32
activation: relu

[2023-01-25 10:53:29,020][HYDRA] 	#1 : +activation=relu num_layers=1 num_hidden=[64]
num_layers: 1
num_hidden:
- 64
activation: relu

[2023-01-25 10:53:29,291][HYDRA] 	#2 : +activation=relu num_layers=2 num_hidden=[32, 32]
num_layers: 2
num_hidden:
- 32
- 32
activation: relu

[2023-01-25 10:53:29,533][HYDRA] 	#3 : +activation=relu num_layers=2 num_hidden=[32, 64]
num_layers: 2
num_hidden:
- 32
- 64
activation: relu

[2023-01-25 10:53:29,777][HYDRA] 	#4 : +activation=relu num_layers=2 num_hidden=[64, 32]
num_layers: 2
num_hidden:
- 64
- 32
activation: relu

[2023-01-25 10:53:30,052][HYDRA] 	#5 : +activation=relu num_layers=2 num_hidden=[64, 64]
num_layers: 2
num_hidden:
- 64
- 64
activation: relu

[2023-01-25 10:53:30,317][HYDRA] 	#6 : +activation=relu num_layers=3 num_hidden=[32, 32, 32]
num_layers: 3
num_hidden:
- 32
- 32
- 32
activation: relu

[2023-01-25 10:53:30,587][HYDRA] 	#7 : +activation=relu num_layers=3 num_hidden=[32, 32, 64]
num_layers: 3
num_hidden:
- 32
- 32
- 64
activation: relu

[2023-01-25 10:53:30,848][HYDRA] 	#8 : +activation=relu num_layers=3 num_hidden=[32, 64, 32]
num_layers: 3
num_hidden:
- 32
- 64
- 32
activation: relu

[2023-01-25 10:53:31,125][HYDRA] 	#9 : +activation=relu num_layers=3 num_hidden=[32, 64, 64]
num_layers: 3
num_hidden:
- 32
- 64
- 64
activation: relu

[2023-01-25 10:53:31,365][HYDRA] 	#10 : +activation=relu num_layers=3 num_hidden=[64, 32, 32]
num_layers: 3
num_hidden:
- 64
- 32
- 32
activation: relu

[2023-01-25 10:53:31,637][HYDRA] 	#11 : +activation=relu num_layers=3 num_hidden=[64, 32, 64]
num_layers: 3
num_hidden:
- 64
- 32
- 64
activation: relu

[2023-01-25 10:53:31,920][HYDRA] 	#12 : +activation=relu num_layers=3 num_hidden=[64, 64, 32]
num_layers: 3
num_hidden:
- 64
- 64
- 32
activation: relu

[2023-01-25 10:53:32,183][HYDRA] 	#13 : +activation=relu num_layers=3 num_hidden=[64, 64, 64]
num_layers: 3
num_hidden:
- 64
- 64
- 64
activation: relu

[2023-01-25 10:53:32,459][HYDRA] 	#14 : +activation=tanh num_layers=1 num_hidden=[32]
num_layers: 1
num_hidden:
- 32
activation: tanh

[2023-01-25 10:53:32,691][HYDRA] 	#15 : +activation=tanh num_layers=1 num_hidden=[64]
num_layers: 1
num_hidden:
- 64
activation: tanh

[2023-01-25 10:53:32,994][HYDRA] 	#16 : +activation=tanh num_layers=2 num_hidden=[32, 32]
num_layers: 2
num_hidden:
- 32
- 32
activation: tanh

[2023-01-25 10:53:33,246][HYDRA] 	#17 : +activation=tanh num_layers=2 num_hidden=[32, 64]
num_layers: 2
num_hidden:
- 32
- 64
activation: tanh

[2023-01-25 10:53:33,499][HYDRA] 	#18 : +activation=tanh num_layers=2 num_hidden=[64, 32]
num_layers: 2
num_hidden:
- 64
- 32
activation: tanh

[2023-01-25 10:53:33,818][HYDRA] 	#19 : +activation=tanh num_layers=2 num_hidden=[64, 64]
num_layers: 2
num_hidden:
- 64
- 64
activation: tanh

[2023-01-25 10:53:34,092][HYDRA] 	#20 : +activation=tanh num_layers=3 num_hidden=[32, 32, 32]
num_layers: 3
num_hidden:
- 32
- 32
- 32
activation: tanh

[2023-01-25 10:53:34,355][HYDRA] 	#21 : +activation=tanh num_layers=3 num_hidden=[32, 32, 64]
num_layers: 3
num_hidden:
- 32
- 32
- 64
activation: tanh

[2023-01-25 10:53:34,619][HYDRA] 	#22 : +activation=tanh num_layers=3 num_hidden=[32, 64, 32]
num_layers: 3
num_hidden:
- 32
- 64
- 32
activation: tanh

[2023-01-25 10:53:34,841][HYDRA] 	#23 : +activation=tanh num_layers=3 num_hidden=[32, 64, 64]
num_layers: 3
num_hidden:
- 32
- 64
- 64
activation: tanh

[2023-01-25 10:53:35,094][HYDRA] 	#24 : +activation=tanh num_layers=3 num_hidden=[64, 32, 32]
num_layers: 3
num_hidden:
- 64
- 32
- 32
activation: tanh

[2023-01-25 10:53:35,294][HYDRA] 	#25 : +activation=tanh num_layers=3 num_hidden=[64, 32, 64]
num_layers: 3
num_hidden:
- 64
- 32
- 64
activation: tanh

[2023-01-25 10:53:35,470][HYDRA] 	#26 : +activation=tanh num_layers=3 num_hidden=[64, 64, 32]
num_layers: 3
num_hidden:
- 64
- 64
- 32
activation: tanh

[2023-01-25 10:53:35,646][HYDRA] 	#27 : +activation=tanh num_layers=3 num_hidden=[64, 64, 64]
num_layers: 3
num_hidden:
- 64
- 64
- 64
activation: tanh
```

</details>

### Remove duplicate configurations

To prevent duplicate configurations from being launched (potentially due to combines with command line overrides), set `hydra.sweeper.remove_duplicates` to `true`. Running the [example](https://github.com/WodkaRHR/hydra_python_lancher/blob/main/example/train.py) with `python example/train.py --config-name multilayer -m +activation=relu,relu hydra.sweeper.remove_duplicates=true` launches the configured jobs.

<details>
    <summary>Experiment invocation and output</summary>

```
[2023-01-25 11:10:47,779][HYDRA] PythonSweeper(max_batch_size=None, entrypoints=['config.multilayer.configure']) sweeping
[2023-01-25 11:10:47,781][HYDRA] Sweep output dir : multirun/2023-01-25/11-10-47
[2023-01-25 11:10:49,107][HYDRA] Launching 14 jobs locally
[2023-01-25 11:10:49,107][HYDRA] 	#0 : +activation=relu num_layers=1 num_hidden=[32]
num_layers: 1
num_hidden:
- 32
activation: relu

[2023-01-25 11:10:49,376][HYDRA] 	#1 : +activation=relu num_layers=1 num_hidden=[64]
num_layers: 1
num_hidden:
- 64
activation: relu

[2023-01-25 11:10:49,643][HYDRA] 	#2 : +activation=relu num_layers=2 num_hidden=[32, 32]
num_layers: 2
num_hidden:
- 32
- 32
activation: relu

[2023-01-25 11:10:49,930][HYDRA] 	#3 : +activation=relu num_layers=2 num_hidden=[32, 64]
num_layers: 2
num_hidden:
- 32
- 64
activation: relu

[2023-01-25 11:10:50,178][HYDRA] 	#4 : +activation=relu num_layers=2 num_hidden=[64, 32]
num_layers: 2
num_hidden:
- 64
- 32
activation: relu

[2023-01-25 11:10:50,427][HYDRA] 	#5 : +activation=relu num_layers=2 num_hidden=[64, 64]
num_layers: 2
num_hidden:
- 64
- 64
activation: relu

[2023-01-25 11:10:50,678][HYDRA] 	#6 : +activation=relu num_layers=3 num_hidden=[32, 32, 32]
num_layers: 3
num_hidden:
- 32
- 32
- 32
activation: relu

[2023-01-25 11:10:50,962][HYDRA] 	#7 : +activation=relu num_layers=3 num_hidden=[32, 32, 64]
num_layers: 3
num_hidden:
- 32
- 32
- 64
activation: relu

[2023-01-25 11:10:51,210][HYDRA] 	#8 : +activation=relu num_layers=3 num_hidden=[32, 64, 32]
num_layers: 3
num_hidden:
- 32
- 64
- 32
activation: relu

[2023-01-25 11:10:51,458][HYDRA] 	#9 : +activation=relu num_layers=3 num_hidden=[32, 64, 64]
num_layers: 3
num_hidden:
- 32
- 64
- 64
activation: relu

[2023-01-25 11:10:51,748][HYDRA] 	#10 : +activation=relu num_layers=3 num_hidden=[64, 32, 32]
num_layers: 3
num_hidden:
- 64
- 32
- 32
activation: relu

[2023-01-25 11:10:52,007][HYDRA] 	#11 : +activation=relu num_layers=3 num_hidden=[64, 32, 64]
num_layers: 3
num_hidden:
- 64
- 32
- 64
activation: relu

[2023-01-25 11:10:52,271][HYDRA] 	#12 : +activation=relu num_layers=3 num_hidden=[64, 64, 32]
num_layers: 3
num_hidden:
- 64
- 64
- 32
activation: relu

[2023-01-25 11:10:52,513][HYDRA] 	#13 : +activation=relu num_layers=3 num_hidden=[64, 64, 64]
num_layers: 3
num_hidden:
- 64
- 64
- 64
activation: relu
```

</details>

### Multiple entrypoints

One can also define multiple entrypoints to generate a cartesian product of configurations between them (and the command line interface overrides). To that end, define multiple entrypoints in `hydra.sweeper.entrypoints`. Running the [example](https://github.com/WodkaRHR/hydra_python_lancher/blob/main/example/train.py) with `python example/train.py --config-name multilayer -m hydra.sweeper.entrypoints=[config.multilayer.configure, config.multilayer.configure_batch_norm]` combines two entrypoints.

<details>
    <summary>Experiment invocation and output</summary>

``` 
[2023-01-25 14:04:15,357][HYDRA] PythonSweeper(max_batch_size=None, entrypoint=['config.multilayer.configure', 'config.multilayer.configure_batch_norm']) sweeping
[2023-01-25 14:04:15,359][HYDRA] Sweep output dir : multirun/2023-01-25/14-04-15
[2023-01-25 14:04:18,259][HYDRA] Launching 28 jobs locally
[2023-01-25 14:04:18,259][HYDRA] 	#0 : num_layers=1 num_hidden=[32] +batch_norm=True
num_layers: 1
num_hidden:
- 32
batch_norm: true

[2023-01-25 14:04:18,517][HYDRA] 	#1 : num_layers=1 num_hidden=[32] +batch_norm=False
num_layers: 1
num_hidden:
- 32
batch_norm: false

[2023-01-25 14:04:18,786][HYDRA] 	#2 : num_layers=1 num_hidden=[64] +batch_norm=True
num_layers: 1
num_hidden:
- 64
batch_norm: true

[2023-01-25 14:04:19,064][HYDRA] 	#3 : num_layers=1 num_hidden=[64] +batch_norm=False
num_layers: 1
num_hidden:
- 64
batch_norm: false

[2023-01-25 14:04:19,296][HYDRA] 	#4 : num_layers=2 num_hidden=[32, 32] +batch_norm=True
num_layers: 2
num_hidden:
- 32
- 32
batch_norm: true

[2023-01-25 14:04:19,574][HYDRA] 	#5 : num_layers=2 num_hidden=[32, 32] +batch_norm=False
num_layers: 2
num_hidden:
- 32
- 32
batch_norm: false

[2023-01-25 14:04:19,839][HYDRA] 	#6 : num_layers=2 num_hidden=[32, 64] +batch_norm=True
num_layers: 2
num_hidden:
- 32
- 64
batch_norm: true

[2023-01-25 14:04:20,084][HYDRA] 	#7 : num_layers=2 num_hidden=[32, 64] +batch_norm=False
num_layers: 2
num_hidden:
- 32
- 64
batch_norm: false

[2023-01-25 14:04:20,306][HYDRA] 	#8 : num_layers=2 num_hidden=[64, 32] +batch_norm=True
num_layers: 2
num_hidden:
- 64
- 32
batch_norm: true

[2023-01-25 14:04:20,640][HYDRA] 	#9 : num_layers=2 num_hidden=[64, 32] +batch_norm=False
num_layers: 2
num_hidden:
- 64
- 32
batch_norm: false

[2023-01-25 14:04:20,907][HYDRA] 	#10 : num_layers=2 num_hidden=[64, 64] +batch_norm=True
num_layers: 2
num_hidden:
- 64
- 64
batch_norm: true

[2023-01-25 14:04:21,136][HYDRA] 	#11 : num_layers=2 num_hidden=[64, 64] +batch_norm=False
num_layers: 2
num_hidden:
- 64
- 64
batch_norm: false

[2023-01-25 14:04:21,377][HYDRA] 	#12 : num_layers=3 num_hidden=[32, 32, 32] +batch_norm=True
num_layers: 3
num_hidden:
- 32
- 32
- 32
batch_norm: true

[2023-01-25 14:04:21,633][HYDRA] 	#13 : num_layers=3 num_hidden=[32, 32, 32] +batch_norm=False
num_layers: 3
num_hidden:
- 32
- 32
- 32
batch_norm: false

[2023-01-25 14:04:21,901][HYDRA] 	#14 : num_layers=3 num_hidden=[32, 32, 64] +batch_norm=True
num_layers: 3
num_hidden:
- 32
- 32
- 64
batch_norm: true

[2023-01-25 14:04:22,188][HYDRA] 	#15 : num_layers=3 num_hidden=[32, 32, 64] +batch_norm=False
num_layers: 3
num_hidden:
- 32
- 32
- 64
batch_norm: false

[2023-01-25 14:04:22,441][HYDRA] 	#16 : num_layers=3 num_hidden=[32, 64, 32] +batch_norm=True
num_layers: 3
num_hidden:
- 32
- 64
- 32
batch_norm: true

[2023-01-25 14:04:22,696][HYDRA] 	#17 : num_layers=3 num_hidden=[32, 64, 32] +batch_norm=False
num_layers: 3
num_hidden:
- 32
- 64
- 32
batch_norm: false

[2023-01-25 14:04:22,948][HYDRA] 	#18 : num_layers=3 num_hidden=[32, 64, 64] +batch_norm=True
num_layers: 3
num_hidden:
- 32
- 64
- 64
batch_norm: true

[2023-01-25 14:04:23,222][HYDRA] 	#19 : num_layers=3 num_hidden=[32, 64, 64] +batch_norm=False
num_layers: 3
num_hidden:
- 32
- 64
- 64
batch_norm: false

[2023-01-25 14:04:23,456][HYDRA] 	#20 : num_layers=3 num_hidden=[64, 32, 32] +batch_norm=True
num_layers: 3
num_hidden:
- 64
- 32
- 32
batch_norm: true

[2023-01-25 14:04:23,678][HYDRA] 	#21 : num_layers=3 num_hidden=[64, 32, 32] +batch_norm=False
num_layers: 3
num_hidden:
- 64
- 32
- 32
batch_norm: false

[2023-01-25 14:04:23,897][HYDRA] 	#22 : num_layers=3 num_hidden=[64, 32, 64] +batch_norm=True
num_layers: 3
num_hidden:
- 64
- 32
- 64
batch_norm: true

[2023-01-25 14:04:24,126][HYDRA] 	#23 : num_layers=3 num_hidden=[64, 32, 64] +batch_norm=False
num_layers: 3
num_hidden:
- 64
- 32
- 64
batch_norm: false

[2023-01-25 14:04:24,356][HYDRA] 	#24 : num_layers=3 num_hidden=[64, 64, 32] +batch_norm=True
num_layers: 3
num_hidden:
- 64
- 64
- 32
batch_norm: true

[2023-01-25 14:04:24,650][HYDRA] 	#25 : num_layers=3 num_hidden=[64, 64, 32] +batch_norm=False
num_layers: 3
num_hidden:
- 64
- 64
- 32
batch_norm: false

[2023-01-25 14:04:24,915][HYDRA] 	#26 : num_layers=3 num_hidden=[64, 64, 64] +batch_norm=True
num_layers: 3
num_hidden:
- 64
- 64
- 64
batch_norm: true

[2023-01-25 14:04:25,171][HYDRA] 	#27 : num_layers=3 num_hidden=[64, 64, 64] +batch_norm=False
num_layers: 3
num_hidden:
- 64
- 64
- 64
batch_norm: false
````
</details>

### Subconfigurations

You might want to combine different configurations defined in python code. This can be entirely realized within the python configuration defined as an endpoint using the `hydra_plugins.python_sweeper_plugin.utils.merge_overrides` method. It takes an arbitrary amount of `Iterable` of `Iterable` of `Tuple` (i.e. configurations returned by an entrypoint) and combines them as a cartesian product. Example:

```
# directory tree
|---- my_app.py
|---- config
|        |---- subconfig
|        |         |------ subconfig.py
|        |----- config.py
```

Let `config/subconfig/subconfig.py` define a `configure()` entrypoint. It could be used by the `config/config.py` configration as follows:

```python
# config/config.py

from hydra_plugins.python_sweeper_plugin.utils import merge_overrides

def configure():
    overrides = []
    # ... build some overrides

    from .subconfig import subconfig
    return merge_overrides(overrides, subconfig.configure())
```

As the `merge_overrides` method produces a valid return value for entrypoints, it can also be used recursively, e.g. `merge_overrides(overrides1, merge_overrides(overrides2, overrides3))`. Note that `merge_overrides(arg1, arg2, ..., argN)` is equivalent to `merge_overrides(arg1, merge_overrides(arg2, ..., merge_overrides(argN-1, argN)...))`, as each call creates a cartesian product between all its arguments.

Running the [example](https://github.com/WodkaRHR/hydra_python_lancher/blob/main/example/train.py) with `python example/train.py --config-name multilayer -m hydra.sweeper.entrypoints=[config.multilayer.configure_with_subconfig]` launches the configured jobs.

<details>
    <summary>Experiment invocation and output</summary>

```
[2023-01-25 14:23:33,921][HYDRA] PythonSweeper(max_batch_size=None, entrypoint=['config.multilayer.configure_with_subconfig']) sweeping
[2023-01-25 14:23:33,923][HYDRA] Sweep output dir : multirun/2023-01-25/14-23-33
[2023-01-25 14:23:36,443][HYDRA] Launching 28 jobs locally
[2023-01-25 14:23:36,443][HYDRA] 	#0 : num_layers=1 num_hidden=[32] +dropout=0.1
num_layers: 1
num_hidden:
- 32
dropout: 0.1

[2023-01-25 14:23:36,674][HYDRA] 	#1 : num_layers=1 num_hidden=[32] +dropout=0.5
num_layers: 1
num_hidden:
- 32
dropout: 0.5

[2023-01-25 14:23:36,907][HYDRA] 	#2 : num_layers=1 num_hidden=[64] +dropout=0.1
num_layers: 1
num_hidden:
- 64
dropout: 0.1

[2023-01-25 14:23:37,158][HYDRA] 	#3 : num_layers=1 num_hidden=[64] +dropout=0.5
num_layers: 1
num_hidden:
- 64
dropout: 0.5

[2023-01-25 14:23:37,380][HYDRA] 	#4 : num_layers=2 num_hidden=[32, 32] +dropout=0.1
num_layers: 2
num_hidden:
- 32
- 32
dropout: 0.1

[2023-01-25 14:23:37,592][HYDRA] 	#5 : num_layers=2 num_hidden=[32, 32] +dropout=0.5
num_layers: 2
num_hidden:
- 32
- 32
dropout: 0.5

[2023-01-25 14:23:37,777][HYDRA] 	#6 : num_layers=2 num_hidden=[32, 64] +dropout=0.1
num_layers: 2
num_hidden:
- 32
- 64
dropout: 0.1

[2023-01-25 14:23:37,970][HYDRA] 	#7 : num_layers=2 num_hidden=[32, 64] +dropout=0.5
num_layers: 2
num_hidden:
- 32
- 64
dropout: 0.5

[2023-01-25 14:23:38,162][HYDRA] 	#8 : num_layers=2 num_hidden=[64, 32] +dropout=0.1
num_layers: 2
num_hidden:
- 64
- 32
dropout: 0.1

[2023-01-25 14:23:38,371][HYDRA] 	#9 : num_layers=2 num_hidden=[64, 32] +dropout=0.5
num_layers: 2
num_hidden:
- 64
- 32
dropout: 0.5

[2023-01-25 14:23:38,546][HYDRA] 	#10 : num_layers=2 num_hidden=[64, 64] +dropout=0.1
num_layers: 2
num_hidden:
- 64
- 64
dropout: 0.1

[2023-01-25 14:23:38,741][HYDRA] 	#11 : num_layers=2 num_hidden=[64, 64] +dropout=0.5
num_layers: 2
num_hidden:
- 64
- 64
dropout: 0.5

[2023-01-25 14:23:38,920][HYDRA] 	#12 : num_layers=3 num_hidden=[32, 32, 32] +dropout=0.1
num_layers: 3
num_hidden:
- 32
- 32
- 32
dropout: 0.1

[2023-01-25 14:23:39,098][HYDRA] 	#13 : num_layers=3 num_hidden=[32, 32, 32] +dropout=0.5
num_layers: 3
num_hidden:
- 32
- 32
- 32
dropout: 0.5

[2023-01-25 14:23:39,299][HYDRA] 	#14 : num_layers=3 num_hidden=[32, 32, 64] +dropout=0.1
num_layers: 3
num_hidden:
- 32
- 32
- 64
dropout: 0.1

[2023-01-25 14:23:39,473][HYDRA] 	#15 : num_layers=3 num_hidden=[32, 32, 64] +dropout=0.5
num_layers: 3
num_hidden:
- 32
- 32
- 64
dropout: 0.5

[2023-01-25 14:23:39,663][HYDRA] 	#16 : num_layers=3 num_hidden=[32, 64, 32] +dropout=0.1
num_layers: 3
num_hidden:
- 32
- 64
- 32
dropout: 0.1

[2023-01-25 14:23:39,909][HYDRA] 	#17 : num_layers=3 num_hidden=[32, 64, 32] +dropout=0.5
num_layers: 3
num_hidden:
- 32
- 64
- 32
dropout: 0.5

[2023-01-25 14:23:40,156][HYDRA] 	#18 : num_layers=3 num_hidden=[32, 64, 64] +dropout=0.1
num_layers: 3
num_hidden:
- 32
- 64
- 64
dropout: 0.1

[2023-01-25 14:23:40,396][HYDRA] 	#19 : num_layers=3 num_hidden=[32, 64, 64] +dropout=0.5
num_layers: 3
num_hidden:
- 32
- 64
- 64
dropout: 0.5

[2023-01-25 14:23:40,581][HYDRA] 	#20 : num_layers=3 num_hidden=[64, 32, 32] +dropout=0.1
num_layers: 3
num_hidden:
- 64
- 32
- 32
dropout: 0.1

[2023-01-25 14:23:40,754][HYDRA] 	#21 : num_layers=3 num_hidden=[64, 32, 32] +dropout=0.5
num_layers: 3
num_hidden:
- 64
- 32
- 32
dropout: 0.5

[2023-01-25 14:23:40,941][HYDRA] 	#22 : num_layers=3 num_hidden=[64, 32, 64] +dropout=0.1
num_layers: 3
num_hidden:
- 64
- 32
- 64
dropout: 0.1

[2023-01-25 14:23:41,129][HYDRA] 	#23 : num_layers=3 num_hidden=[64, 32, 64] +dropout=0.5
num_layers: 3
num_hidden:
- 64
- 32
- 64
dropout: 0.5

[2023-01-25 14:23:41,318][HYDRA] 	#24 : num_layers=3 num_hidden=[64, 64, 32] +dropout=0.1
num_layers: 3
num_hidden:
- 64
- 64
- 32
dropout: 0.1

[2023-01-25 14:23:41,514][HYDRA] 	#25 : num_layers=3 num_hidden=[64, 64, 32] +dropout=0.5
num_layers: 3
num_hidden:
- 64
- 64
- 32
dropout: 0.5

[2023-01-25 14:23:41,718][HYDRA] 	#26 : num_layers=3 num_hidden=[64, 64, 64] +dropout=0.1
num_layers: 3
num_hidden:
- 64
- 64
- 64
dropout: 0.1

[2023-01-25 14:23:41,929][HYDRA] 	#27 : num_layers=3 num_hidden=[64, 64, 64] +dropout=0.5
num_layers: 3
num_hidden:
- 64
- 64
- 64
dropout: 0.5
```

</details>
