## Pre-requistes 

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
$ pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 
```

### Note
> perf_event_paranoid:
> Controls use of the performance events system by unprivileged users (without CAP_SYS_ADMIN). The default value is 2. <br/>
> $ -1$: Allow use of (almost) all events by all users Ignore mlock limit after perf_event_mlock_kb without CAP_IPC_LOCK<br/>
> $\ge 0$ : Disallow ftrace function tracepoint by users without CAP_SYS_ADMIN Disallow raw tracepoint access by users without CAP_SYS_ADMIN<br/>
> $\ge 1$: Disallow CPU event access by users without CAP_SYS_ADMIN<br/>
> $\ge 2$: Disallow kernel profiling by users without CAP_SYS_ADMIN<br/>