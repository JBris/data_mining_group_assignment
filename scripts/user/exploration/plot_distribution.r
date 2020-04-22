library(ggplot2)
library(tidyverse)
library(readr)
library(scales)

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

####################################################################################

plot_scaled_data <- function (data, title) {
  data %>% 
    ungroup() %>% 
    mutate(g = g %>% as.integer()) %>% 
    group_by(g) %>%
    ggplot(aes(x=t, y=v)) +
    geom_line(aes(group=g, color=g)) +
    labs(x='Date Time', y='Power Usage (kWh)',
         color=NULL)+theme(legend.position = 'bottom') +
    ggtitle(title) + 
    facet_wrap(~ g) + theme(
      axis.text.y=element_blank(),
      axis.text.x=element_blank(),
      axis.ticks.x=element_blank(), 
      axis.ticks.y=element_blank(), 
      panel.background=element_blank(),
      panel.border=element_blank(),
      panel.grid.major=element_blank(),
      panel.grid.minor=element_blank(),
      plot.background=element_blank()
    ) 
}

standardized_data <- data %>%
  group_by(s= site, g = channel_id) %>%
  mutate(v = scale(usage), t = date_time) %>%
  select(s, g, v, t)

standardized_data <- standardized_data %>% filter(v < 10 & v > -10)
plot_scaled_data(standardized_data, "Standardized Power Usage by Date Time")

standardized_daily_data <- data %>%
  group_by(s = site, g = channel_id, t = cut(date_time, "24 hour")) %>%
  mutate(v = scale(usage)) %>%
  summarise(v = mean(v))

plot_scaled_data(standardized_daily_data, "Standardized Daily Power Usage by Date Time")

####################################################################################

normalized_data <- data %>%
  group_by(s= site, g = channel_id) %>%
  mutate(v = tanh(usage), t = date_time) %>%
  select(s, g, v, t)

plot_scaled_data(normalized_data, "Normalized Power Usage by Date Time")

normalized_daily_data <- data %>%
  group_by(s = site, g = channel_id, t = cut(date_time, "24 hour")) %>%
  mutate(v = tanh(usage)) %>%
  summarise(v = mean(v))

plot_scaled_data(normalized_daily_data, "Normalized Daily Power Usage by Date Time")
