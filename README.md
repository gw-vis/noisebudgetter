## noisebudgetter

- `NoiseBudgetter` is a tool to make a noise badget, which is an overlap of many kinds of noise sources.

- Originally, this tool was developed by Ayaka Shoda.

- [Noise Budgetter on JGW wiki](http://gwwiki.icrr.u-tokyo.ac.jp/JGWwiki/KAGRA/Commissioning/NoiseBudgetter)

- This tool is running on Django.
  - [official document of Django (Japanese)](https://docs.djangoproject.com/ja/2.2/intro/tutorial01/)

### how to launch

```
% ssh k1ctr7
% conda activate django-env
% cd /kagra/Dropbox/Personal/Shoda/src/AppTest/
% nohup python manage.py runserver 0.0.0.0:8000 > nohup.out &
```

### current task

- (Yuzurihara)
  - understand the code
  - test the possibility that the tool can move from `k1ctr7` to another computer
    - yes, it's possible.Because this tool needs to read full data, the tool needs `k1nds2` or cache file system.
  - summarize the necessary codes on github (https://github.com/gw-vis/noisebudgetter).
