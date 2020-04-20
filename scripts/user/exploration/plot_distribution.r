library(ggplot2)
library(tidyverse)
library(readr)

data <- read_csv("data/processed_dataset.csv") %>%   
  mutate(
    site = as.factor(site),
    channel_id = as.factor(channel_id),
    date_time = as.POSIXct(date_time, format="%d/%m/%Y %H:%M", tz="UTC"),
  )  

####################################################################################

# Plotting distribution 

ggplot(data, aes(x=date_time, y=usage)) +
  geom_line(aes(group=site, color=site)) +
  labs(x='Date Time', y='Power Usage (kWh)',
       color=NULL)+theme(legend.position = 'bottom')

####################################################################################

# Plotting filtered distribution 

data <- data %>% filter(usage >= 0, usage < 10000)

ggplot(data, aes(x=date_time, y=usage)) +
  geom_line(aes(group=site, color=site)) +
  labs(x='Date Time', y='Power Usage (kWh)',
       color=NULL)+theme(legend.position = 'bottom')

ggplot(data, aes(x=date_time, y=usage)) +
  geom_line(aes(group=channel_id, color=channel_id)) +
  labs(x='Date Time', y='Power Usage (kWh)',
       color=NULL)+theme(legend.position = 'bottom')

####################################################################################

# Grouping time intervals by day

project_summary <- function(group, interval) {
  project_ts <- data %>%
    group_by(g = !!group, t = cut(date_time, interval)) %>%
    summarise(v = mean(usage))
    
  project_ts$t <- project_ts$t %>% as.Date(format="%Y-%m-%d")
  
  project_ts %>% ggplot(aes(x=t, y=v)) +
    geom_line(aes(group=g, color=g)) +
    labs(x='Date Time', y='Power Usage (kWh)',
         color=NULL)+theme(legend.position = 'bottom')
}

project_summary(data$site, "24 hour")
project_summary(data$channel_id, "24 hour")
