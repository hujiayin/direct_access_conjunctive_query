# Direct Access and Single Access (Selection)

This repository is the implementation of Direct Access and Single Access(Selection) Algorithms for access the k-th records of conjunctive query with tractable order. 

## Lexicographic Order 
Currently, we have done the Direct Access and Single Access for tractable lexicographic order. To know the detailed theory and algorithm, please check [Tractable Orders for Direct Access to Ranked Answers of Conjunctive Queries](https://dl.acm.org/doi/10.1145/3578517)

## Programming Language and Database Settings
The project is developed in Python(3.12). To run the examples and experiments, please create the environment and install the necessary dependencies. 
```
python -m venv .selectk_env
source .selectk_env/bin/activate
pip install -r requirements.txt
```

The database system using in the experiments is PostgreSQL 17.4 ([Download](/https://www.postgresql.org/download/)). For our experiments, some configurations need to be modified. We use the setting 
```
# change in postgresql.conf
work_mem="2G"
statement_timeout=3600000
```


## Examples 
We provide some small examples in [examples](examples). To get the results, use the following command to run all the examples we provides. 
```
bash examples/run_examples.sh 
```
User can use their own data and query aligned with the format of examples. Please change the default path as your own example in [Direct Access Running Template](examples/template_directaccess.sh) and [Single Access Running Template](examples/template_select.sh). 
```
bash examples/template_directaccess.sh
bash examples/template_select.sh
```
## Experiments
