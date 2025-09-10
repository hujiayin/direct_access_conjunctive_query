# Direct Access and Single Access (Selection)

This repository contains an implementation of Direct Access and Single Access (also called Selection) algorithms for accessing the k-th answer of a Conjunctive Query (also known as a Select-Project-Join Query) under a specified order. The supported order can be:
1. A lexicographic orders on the attributes
2. A sum of attributes

We have implemented the efficient algorithms from [Tractable Orders for Direct Access to Ranked Answers of Conjunctive Queries](https://dl.acm.org/doi/10.1145/3578517) and [Efficient Computation of Quantiles over Joins](https://dl.acm.org/doi/10.1145/3584372.3588670). The provided query and order are automatically analyzed to check if they fall into the tractable cases described in these papers.

## Programming Language and Database Settings
The project is developed in Python(3.12). To run the examples and experiments, please create the environment and install the necessary dependencies. 
```
python -m venv .selectk_env
source .selectk_env/bin/activate
pip install -r requirements.txt
```

The database system used in the experiments is PostgreSQL 17.4 ([Download](/https://www.postgresql.org/download/)). For our experiments, the database configuration is modified. We use the following settings: 
```
# change in postgresql.conf
work_mem="2G"
statement_timeout=3600000
```


## Examples 
We provide some small examples under the [examples](examples) directory. To get the results, use the following command to run all the examples we provide. 
```
bash examples/run_examples.sh 
```
A user can use their own data and query aligned with the format in the examples. Please change the default path as your own example in [Direct Access Running Template](examples/template_directaccess.sh) and [Single Access Running Template](examples/template_select.sh). 
```
bash examples/template_directaccess.sh
bash examples/template_select.sh
```
## Experiments
