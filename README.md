### Creating Data Science Framework

This framework would be helpful to know different packages available in different languages. 
Currently I am trying to cover same analysis using the following languages and prepare a comparison study between them.

* R
* python
* Julia
* scala

The directory set up is as follows:
```
data_science_framework:
Project/
|
|-- config/
|      |-- model_config_param.json: Details of model hyperparameter min/max level etc.
|      |-- database_config.json: Details of data base configurations.
|
|-- data/
|      |-- inputs: Keep input files
|      |-- outputs/
|             |-- charts: Visual outputs will be saved in this folder.
|             |-- table: csv/txt summary outputs will be saved in this folder.
|      |-- interim:
|
|-- documents/
|      |-- literature:
|      |-- Excel Template: Naming Convention YYYYMMDD_NAME_OF_FILE_INITIALS_VER.xlsb
|      |-- Powerpoint:Naming Convention YYYYMMDD_NAME_OF_FILE_INITIALS_VER
|
|-- logs/
|      |-- etl_logs:
|      |-- model_performance_logs:
|      |-- visualization_logs:
|
|-- src
|      |-- r: R-codes
|      |-- python: python-codes
|             |-- __init__.py
|             |-- etl
|                   |-- reading_input_files.py
|                   |-- data_transformation.py
|             |-- models
|             |-- visualization
|      |-- julia: Julia-codes
|      |-- scala: scala-codes
|
|-- requirements.txt       
       
```
