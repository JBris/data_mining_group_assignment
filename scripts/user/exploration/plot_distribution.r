library(ggplot2)
library(tidyverse)
library(readr)

data <- read_csv("data/processed_dataset.csv")
data$site_group <- as.factor(data$site)
data$channel_id_group <- as.factor(data$channel_id)
data$date <- data$date_time
data$date_time <- as.Date(data$date_time, format="%d/%m/%Y %H:%M")
data$timestamp <- as.POSIXct(data$date, format="%d/%m/%Y %H:%M", tz="UTC")

####################################################################################

# Plotting distribution 

ggplot(data, aes(x=date_time, y=usage)) +
  geom_line(aes(group=site_group, color=site_group)) +
  labs(x='Date Time', y='Power Usage (kWh)',
       color=NULL)+theme(legend.position = 'bottom')

####################################################################################

# Plotting filtered distribution 

data <- data %>% filter(usage >= 0, usage < 10000)

ggplot(data, aes(x=date_time, y=usage)) +
  geom_line(aes(group=site_group, color=site_group)) +
  labs(x='Date Time', y='Power Usage (kWh)',
       color=NULL)+theme(legend.position = 'bottom')

ggplot(data, aes(x=date_time, y=usage)) +
  geom_line(aes(group=channel_id_group, color=channel_id_group)) +
  labs(x='Date Time', y='Power Usage (kWh)',
       color=NULL)+theme(legend.position = 'bottom')

####################################################################################

# Applying smoothers

project_summary <- function(group, interval) {
  project_ts <- data %>%
    group_by(g = !!group, t = cut(timestamp, interval)) %>%
    summarise(v = mean(usage))
  
  project_ts %>% ggplot(aes(x=t, y=v)) +
    geom_line(aes(group=g, color=g)) +
    labs(x='Date Time', y='Power Usage (kWh)',
         color=NULL)+theme(legend.position = 'bottom')
}

project_summary(data$site_group, "24 hour")
project_summary(data$channel_id_group, "24 hour")
