The components of this project are divide in to two components:

* Pruning & Profiling utility [Running Profiling](#running-profiling)
* Data analysis and  Causal graph generation [Python Notebook](#generating-causal-graph) 

## Running Profiling

Accepts one command line argument to store results files(CSV and output)

```bash
 $  python prune-profiler.py --result_dir output/run-1
```

### Pre-requistes 

> [!TIP]
> This below step for perf event setting is only required if we need to gather perf data
>
> perf_event_paranoid:
> Controls use of the performance events system by unprivileged users (without CAP_SYS_ADMIN). The default value is 2. <br/>
> $ -1$: Allow use of (almost) all events by all users Ignore mlock limit after perf_event_mlock_kb without CAP_IPC_LOCK<br/>
> $\ge 0$ : Disallow ftrace function tracepoint by users without CAP_SYS_ADMIN Disallow raw tracepoint access by users without CAP_SYS_ADMIN<br/>
> $\ge 1$: Disallow CPU event access by users without CAP_SYS_ADMIN<br/>
> $\ge 2$: Disallow kernel profiling by users without CAP_SYS_ADMIN<br/>


Since perf requires super-user access and running python with sudo can be troublesome in terms of risk and library dependencies, it will be good to change perf_event_paranoid mode. This need to be done for each system reboot. 
```bash
 $ sudo su
 $ echo "-1" > /proc/sys/kernel/perf_event_paranoid
```

Setup a virtual environment and install prerequistes:
```
$ virtualenv my_env
$ source my_env/bin/activate
$ pip3 install numpy pandas gpustat tqdm
$ pip3 install torch torchvision torchaudio
```

## Generating Causal Graph

Open the python notebook **CausalModeling/DataProcessing.ipynb**

Modify the path to results directory to the location wherein results for analysis stored, and run the full script.

```python
directory = '../PruningProfiler/output/2024-04-18_Vaisakh/final'
```

## TODO

* Modify prune-profiler.py to pass model configuration as arguments or  provide JSON file as input for running variety of configuration automatically
* ~~Make batch-size and runner configuration for imagenet data set configurable as the default setting is resulting in GPU/CUDA OOM desktop/laptop.~~
* ~~Add post processing script to make combined dataframe which can be given for causal modelling.~~
* Instead of 'dmidecode' which requires sudo access, try to obtain the data from other paths (ref: https://unix.stackexchange.com/questions/24212/how-to-get-dmidecode-information-without-root-privileges ), which doesn't require root privilages
* Modify the process creation for prune-runner.py from prune-profiler.py so that the STDOUT is also visible during execution - helpful in seeing progress.
