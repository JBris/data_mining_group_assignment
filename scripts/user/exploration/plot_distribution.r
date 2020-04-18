library(ggplot2)
library(tidyverse)
library(readr)

data <- read_csv("data/processed_dataset.csv")
data$site_group <- as.factor(data$site)
data$channel_id_group <- as.factor(data$channel_id)
data$date_time <- as.Date(data$date_time, format="%d/%m/%Y %H:%M")

ggplot(data, aes(x=date_time, y=usage)) +
  geom_line(aes(group=site_group, color=site_group)) +
  labs(x='Date Time', y='Power Usage (kWh)',
       color=NULL)+theme(legend.position = 'bottom')

data <- data %>% filter(usage >= 0, usage < 10000)

ggplot(data, aes(x=date_time, y=usage)) +
  geom_line(aes(group=site_group, color=site_group)) +
  labs(x='Date Time', y='Power Usage (kWh)',
       color=NULL)+theme(legend.position = 'bottom')

ggplot(data, aes(x=date_time, y=usage)) +
  geom_line(aes(group=channel_id_group, color=channel_id_group)) +
  labs(x='Date Time', y='Power Usage (kWh)',
       color=NULL)+theme(legend.position = 'bottom')
