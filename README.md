# benchmark

simple project to benchmark odoo performance.

## Installation

- install Odoo instances locally. with docky for exemple, for each instance : 
```
docky run

> createdb benchmark
> odoo -d benchmark -i sale,purchase,point_of_sale,delivery,mrp,crm
```

- install python libraries

```
pip install -r requirements.txt
```


## Run

- set setting in the file benchmark.py (odoo URLs, etc...)
- run the script

```
python ./benchmark.py
```


## Expected Result

