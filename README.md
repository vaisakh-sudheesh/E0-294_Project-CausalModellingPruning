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
```bash
$ virtualenv my_env
$ source my_env/bin/activate
$ pip3 install numpy pandas gpustat tqdm notebook
$ pip3 install torch torchvision torchaudio
```

## Generating Causal Graph

Open the python notebook **CausalModeling/DataProcessing.ipynb**

Modify the path to results directory to the location wherein results for analysis stored, and run the full script.

```python
directory = '../PruningProfiler/output/2024-04-18_Vaisakh/final'
```

In case Juypter notebook is not available, you may start a notebook instance as pip has installed a version as part of [Pre-requistes](#pre-requistes):
```bash
$ source my_env/bin/activate
$ jupyter notebook
[I 2024-04-19 03:29:36.915 ServerApp] jupyter_lsp | extension was successfully linked.
[I 2024-04-19 03:29:36.924 ServerApp] jupyter_server_terminals | extension was successfully linked.
[I 2024-04-19 03:29:36.941 ServerApp] jupyterlab | extension was successfully linked.
[I 2024-04-19 03:29:36.966 ServerApp] notebook | extension was successfully linked.
[I 2024-04-19 03:29:37.553 ServerApp] notebook_shim | extension was successfully linked.
[I 2024-04-19 03:29:37.603 ServerApp] notebook_shim | extension was successfully loaded.
[I 2024-04-19 03:29:37.614 ServerApp] jupyter_lsp | extension was successfully loaded.
[I 2024-04-19 03:29:37.620 ServerApp] jupyter_server_terminals | extension was successfully loaded.
[I 2024-04-19 03:29:37.629 LabApp] JupyterLab extension loaded from /root/developer/E0-294_Project-CausalModellingPruning-main/.venv/lib/python3.12/site-packages/jupyterlab
[I 2024-04-19 03:29:37.630 LabApp] JupyterLab application directory is /root/developer/E0-294_Project-CausalModellingPruning-main/.venv/share/jupyter/lab
[I 2024-04-19 03:29:37.633 LabApp] Extension Manager is 'pypi'.
[I 2024-04-19 03:29:37.730 ServerApp] jupyterlab | extension was successfully loaded.
[I 2024-04-19 03:29:37.739 ServerApp] notebook | extension was successfully loaded.
[I 2024-04-19 03:29:37.741 ServerApp] Serving notebooks from local directory: /root/developer/E0-294_Project-CausalModellingPruning-main
[I 2024-04-19 03:29:37.741 ServerApp] Jupyter Server 2.14.0 is running at:
[I 2024-04-19 03:29:37.741 ServerApp] http://localhost:8888/tree?token=1742443546bfad96d62e3bae0c2e20147d5ceaa935e3f4bf
[I 2024-04-19 03:29:37.741 ServerApp]     http://127.0.0.1:8888/tree?token=1742443546bfad96d62e3bae0c2e20147d5ceaa935e3f4bf
[I 2024-04-19 03:29:37.741 ServerApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
[C 2024-04-19 03:29:37.772 ServerApp] 
    
    To access the server, open this file in a browser:
        file:///root/.local/share/jupyter/runtime/jpserver-7512-open.html
    Or copy and paste one of these URLs:
        http://localhost:8888/tree?token=1742443546bfad96d62e3bae0c2e20147d5ceaa935e3f4bf
        http://127.0.0.1:8888/tree?token=1742443546bfad96d62e3bae0c2e20147d5ceaa935e3f4bf
[I 2024-04-19 03:29:37.839 ServerApp] Skipped non-installed server(s): bash-language-server, dockerfile-language-server-nodejs, javascript-typescript-langserver, jedi-language-server, julia-language-server, pyright, python-language-server, python-lsp-server, r-languageserver, sql-language-server, texlab, typescript-language-server, unified-language-server, vscode-css-languageserver-bin, vscode-html-languageserver-bin, vscode-json-languageserver-bin, yaml-language-server
```

The URL link similar to the one listed above can be used in VScode or other IDEs for running executable.

## TODO

* Modify prune-profiler.py to pass model configuration as arguments or  provide JSON file as input for running variety of configuration automatically
* ~~Make batch-size and runner configuration for imagenet data set configurable as the default setting is resulting in GPU/CUDA OOM desktop/laptop.~~
* ~~Add post processing script to make combined dataframe which can be given for causal modelling.~~
* Instead of 'dmidecode' which requires sudo access, try to obtain the data from other paths (ref: https://unix.stackexchange.com/questions/24212/how-to-get-dmidecode-information-without-root-privileges ), which doesn't require root privilages
* Modify the process creation for prune-runner.py from prune-profiler.py so that the STDOUT is also visible during execution - helpful in seeing progress.
