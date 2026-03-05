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
work_mem = 2048MB 
shared_buffers = 2048MB
statement_timeout = 3600000
```
Restart PostgreSQL and active the new configuration after changing. 
```
sudo systemctl restart postgresql
```

## Examples 
We provide some small examples under the [examples](examples) directory. Please check the [Tutorial Notebook](examples/Algorithm_Tutorial.ipynb) for detailed usage. 

## Experiments
Currently we have 3 experiments exploring the 3-way join. 
1. Performance among Direct Access, Single Access and PostgreSQL with different input sizes and different join sizes. 
2. Effect of access position among Direct Access, Single Access and PostgreSQL with full order and single order(as a join attribute). 
3. Change of relative performance between Direct Access and Single Access with different input sizes under different distributions.

To run the experiments 1 & 2, please first set [pg_config.sh](experiments/synthetic_exps/pg_config.sh).

Use the following command to run the experiments. 
```
bash experiments/synthetic_exps/run_exp1.sh > /dev/null 2>&1
bash experiments/synthetic_exps/run_exp2.sh > /dev/null 2>&1
bash experiments/synthetic_exps/run_exp3.sh > /dev/null 2>&1
```