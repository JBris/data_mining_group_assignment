# data_mining_group_assignment


## Table of Contents  

* [Introduction](#introduction) 
* [Data](#data)
* [DataScience](#datascience)
* [InfluxDB](#influxdb) 
* [PostgreSQL](#postgresql)  

## Introduction

This repo contains public resources for the Data Mining group assignment.

**As the provided data for this assignment is confidential, all data sets, images, and models will be inaccessible from this repo.** 

InfluxDB and Grafana are included in the Docker stack for database storage and visualization purposes. 

Postgres and Adminer are also included for those who are unfamiliar with Influx.

If you're using Docker, execute [build.sh](build.sh) to get started.

## Data 

The provided data set should be placed in the [data directory.](scripts/user/data), and renamed to *initial_dataset.csv*. 

The [initial_processing script](scripts/user/data_processing/initial_processing.py) performs some initial processing on the data. It renames the columns, drops unneeded columns, converts channels and sites to factors, and factorizes the channel ID-key pairs.

## DataScience 

The datascience container offers both R and Python packages. A list of R and Python dependencies can be found in the [Dockerfile](Dockerfile). See [requirements.txt](scripts/user/requirements.txt) for the list of Python packages and their respective versions. See [packages.txt](scripts/user/packages.txt) for the list of R packages and their respective versions.

As the [docker-compose.yml](docker-compose.yml) file shows, this repo extends from the [rocker/tidyverse image](https://hub.docker.com/r/rocker/tidyverse) which already includes the tidyverse collection and RStudio server.

If you opt to use Docker, you can view the [Makefile](Makefile) for relevant Docker commands. The `make run` command will allow users to execute shell commands within the datascience container. The `make enter` command will allow users to directly enter the container by starting a new shell.

## InfluxDB

InfluxDB is a time series database. For those who are unfamiliar, more information can be found at [influxdata.com](https://www.influxdata.com/). InfluxDB can be combined with [Grafana](https://grafana.com/) to analyze and visualize the data. View the [.env.example file](.env.example) to configure your InfluxDB & Grafana versions and ports.

CSV files can be easily imported to your InfluxDB instance using the [csv-to-influxdb](https://github.com/fabio-miranda/csv-to-influxdb) package.

## PostgreSQL

Postgres can be used instead of Influx if required. 

Database dumps can be imported and exported using `make dbimp` and `make dbexp` respectively. Dumps can be found in the `data` directory.

`make csvimp` will import CSV files into the database. Ensure that the CSV data is placed in the [data directory](data). Supply the *f* argument to specify the file to use. E.g. `make csvimp f=processed_dataset`.
 
The following settings can be configured in your .env file:

| Name          | Default Value |  
| ------------- |:-------------:|  
| DB_NAME       | project       | 
| DB_USER       | user          |    
| DB_PASSWORD   | pass          |    
| DB_ROOT_PASSWORD | password   |    
| DB_HOST       | postgres      |    
| DB_PORT       | 5432          |    
