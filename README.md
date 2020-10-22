## noisebudgetter
- `NoiseBudgetter` is a tool to make a noise badget, which is an overlap of many kinds of noise sources.

- Originally, this tool was developed by Ayaka Shoda.
  - [Noise Budgetter on JGW wiki](http://gwwiki.icrr.u-tokyo.ac.jp/JGWwiki/KAGRA/Commissioning/NoiseBudgetter)

- This tool is running on Django and python.
  - [official document of Django (Japanese)](https://docs.djangoproject.com/ja/2.2/intro/tutorial01/)

### how to make a anaconda environment for noisebudgetter
- conda-build recipe is here : `/users/yuzu/django-env_20201006.yaml @k1ctr1`
- `conda env create --file django-env_20201006.yaml -n noiseb`
- Because the installed gwpy package is very old (v0.15?), update them
  - `conda install -c conda-forge gwpy`
  - `conda install -c conda-forge ldas-tools-framecpp`
  - `conda install -c conda-forge python-ldas-tools-framecpp`
- enter virtual environment
   - `conda activate noiseb`

### how to launch
- in the case of k1ctr7

``` shell
% ssh k1ctr7
% conda activate django-env
% cd /kagra/Dropbox/Personal/Shoda/src/AppTest/
% nohup python manage.py runserver 0.0.0.0:8000 > nohup.out &
```

### current task
- understand the code
- summarize the necessary codes on github (https://github.com/gw-vis/noisebudgetter).

### finished task
- test the possibility that the tool can move from `k1ctr7` to another computer
  - yes, it's possible.Because this tool needs to read full data, the tool needs `k1nds2` or cache file system.
