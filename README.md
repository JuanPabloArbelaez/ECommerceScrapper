# ECommerceScrapper
Intrepid Interview Test – Jr Data Engineer

### Installation
```
$  mkvirtualenv -p python3.8 venv
(venv) $  pip install -r requirements.txt
```



## Running

##### Scrap example Lazada Product page and save as json
```
(venv) $  python main.py
```

##### Scrap example Lazada Category page and save as json
```
(venv) $  python main.py -s category
```

##### Scrap example Lazada Category page and save as csv
```
(venv) $  python main.py -s category -f csv
```

##### Scrap custom Lazada Product page and save as json
```
(venv) $  python main.py -s product -u <CUSTOM LAZADA PRODUCT URL>
```

##### Scrap custom Lazada Category page and save as csv
```
(venv) $  python main.py -s product -u <CUSTOM LAZADA CATEGORY URL> -f csv
```

##### Scrap custom Lazada Product page and save as json in custom directory
```
(venv) $  python main.py -s product -u <CUSTOM LAZADA PRODUCT URL> -o <CUSTOM OUTPUT DIRECTORY PATH>
```





