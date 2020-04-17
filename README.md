# data_mining_group_assignment


## Table of Contents  

* [Introduction](#introduction)<a name="introduction"/>
* [InfluxDB](#influxdb)<a name="influxdb"/>

### Introduction

This repo contains public resources for the Data Mining group assignment.

InfluxDB and Grafana are included in the Docker stack for data storage and visualization purposes. 

If you're using Docker, execute [build.sh](build.sh) to get started.

### InfluxDB

InfluxDB is a time series database. For those who are unfamiliar, more information can be found at [influxdata.com](https://www.influxdata.com/). InfluxDB can be combined with [Grafana](https://grafana.com/) to analyze and visualize the data. View the [.env.example file](.env.example) to configure your InfluxDB & Grafana versions and ports.

CSV files can be easily imported to your InfluxDB instance using the [csv-to-influxdb](https://github.com/fabio-miranda/csv-to-influxdb) package.
