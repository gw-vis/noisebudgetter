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

### AdminLTE
- Original code used the v2.4.10
  - I updated codes to use v2.4.18
  - It didn't require the modification of code itself
- I don't add this library on this github, to reduce the git repository size

#### to install AdminLTE
- command memo
  - `wget https://github.com/ColorlibHQ/AdminLTE/archive/v2.4.18.zip`
  - `unzip v2.4.18.zip`
  - `cp -r AdminLTE-2.4.18 DjangoApp/NoiseBudgetter/static/`
  - `cp -r AdminLTE-2.4.18 DjangoApp/static_for_deploy`

### how to launch
- on k1ctr7

``` shell
% ssh k1ctr7
% conda activate django-env
% cd /kagra/Dropbox/Personal/Shoda/src/AppTest/
% nohup python manage.py runserver 0.0.0.0:8000 > nohup.out &
```

- on Pastavi server
  - after runnning following commands, visit [http://172.16.34.76:8000/NoiseBudgetter/](http://172.16.34.76:8000/NoiseBudgetter/)

``` shell
% conda activate noiseb
% python manage.py runserver 0.0.0.0:8000
```

### current task
- install Dropbox in the server

### finished task
- test the possibility that the tool can move from `k1ctr7` to another computer
  - yes, it's possible.
  - note that the tool needs `k1nds2` or cache file system to read full data.
  - the measured data, such as transfer function, should be stored in Dropbox. 
- understand the code
- summarize the necessary codes on github (https://github.com/gw-vis/noisebudgetter).

