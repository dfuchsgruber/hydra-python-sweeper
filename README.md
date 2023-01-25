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

Each entrypoint method should take no arguments and return an `Iterable` of `Tuple`s that are the key-value pairs for overriding. The order will be respected when launching jobs.

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

