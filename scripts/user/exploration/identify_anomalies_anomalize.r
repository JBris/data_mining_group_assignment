#Anomaly detection using anomalize stochastic methods

library(readr)
library(tidyverse)
library(dplyr)
library(anomalize)

data <- read_csv("data/final_processed.csv") %>%
  mutate(
    date_time = as.POSIXct(date_time, format="%d/%m/%Y %H:%M", tz="UTC"),
    usage = usage %>% replace_na(0)
  ) %>%
  group_by(channel_id) %>%
  distinct(date_time, .keep_all = T)  %>%
  ungroup()

avg_daily_use <- data %>%
  group_by(g= channel_id, t = cut(date_time, "24 hour")) %>%
  summarise(v = mean(usage))  %>%
  mutate(t = as.POSIXct(t, format="%Y-%m-%d")) %>%
  arrange(t)

avg_daily_use %>% glimpse()

avg_hourly_use <- data %>%
  group_by(g= channel_id, t = cut(date_time, "1 hour")) %>%
  summarise(v = mean(usage))  %>%
  mutate(t = as.POSIXct(t, format="%Y-%m-%d %H:%M:%S", tz="UTC")) %>%
  arrange(t)

avg_hourly_use %>% glimpse()

fifteen_min_use <- data %>%
  group_by(g = channel_id, t = date_time) %>%
  mutate(v = usage) %>%
  select(g, t, v) %>%
  arrange(t)

fifteen_min_use %>% glimpse()

####################################################################################

# Daily outliers

daily_anomalized <- avg_daily_use %>%
  group_by(g) %>%
  time_decompose(
    v, 
    frequency = "1 week", 
    trend = "3 months", 
    method="stl", # or twitter
    merge = TRUE
  ) %>%
  anomalize(
    remainder, 
    method="iqr", # or gesd
    alpha = 0.05
  ) %>% 
  time_recompose()

daily_anomalized %>%
  filter(g <= 10) %>%
  plot_anomalies(ncol = 3, alpha_dots = 0.25, time_recomposed = T)

daily_anomalized %>%
  filter(g > 10 & g <= 20) %>%
  plot_anomalies(ncol = 3, alpha_dots = 0.25, time_recomposed = T)

daily_anomalized %>%
  filter(g > 20 & g <= 30) %>%
  plot_anomalies(ncol = 3, alpha_dots = 0.25, time_recomposed = T)

####################################################################################

# Hourly outliers

c20_hourly_anomalized <- avg_hourly_use %>%
  group_by(g) %>%
  filter(g == 20) %>%
  time_decompose(
    v, 
    frequency = "1 day", 
    trend = "1 month", 
    method="twitter", # or twitter
    merge = TRUE
  ) %>%
  anomalize(
    remainder, 
    method="iqr", # or gesd
    alpha = 0.05
  ) 

c20_hourly_anomalized %>% plot_anomalies(ncol = 3, alpha_dots = 10, time_recomposed = F)

hourly_anomalized <- avg_hourly_use %>%
  group_by(g) %>%
  time_decompose(
    v, 
    frequency = "1 day", 
    trend = "1 month", 
    method="stl", # or twitter
    merge = TRUE
  ) %>%
  anomalize(
    remainder, 
    method="iqr", # or gesd
    alpha = 0.05
  ) %>% 
  time_recompose()

hourly_anomalized %>%
  filter(g <= 10) %>%
  plot_anomalies(ncol = 3, alpha_dots = 0.25, time_recomposed = T)

hourly_anomalized %>%
  filter(g > 10 & g <= 20) %>%
  plot_anomalies(ncol = 3, alpha_dots = 0.25, time_recomposed = T)

hourly_anomalized %>%
  filter(g > 20 & g <= 30) %>%
  plot_anomalies(ncol = 3, alpha_dots = 0.25, time_recomposed = T)

####################################################################################

# 15 minute outliers

c20_fifteen_anomalized <- fifteen_min_use %>%
  group_by(g) %>%
  filter(g == 20) %>%
  time_decompose(
    v, 
    frequency = "1 day", 
    trend = "14 days", 
    method="stl", # or twitter
    merge = TRUE
  ) %>%
  anomalize(
    remainder, 
    method="iqr", # or gesd
    alpha = 0.05
  ) 

c20_fifteen_anomalized %>% plot_anomalies(ncol = 3, alpha_dots = 10, time_recomposed = F)

fifteen_min_anomalized <- fifteen_min_use %>%
  group_by(g) %>%
  time_decompose(
    v, 
    frequency = "1 day", 
    trend = "14 days", 
    method="stl", # or twitter
    merge = TRUE
  ) %>%
  anomalize(
    remainder, 
    method="iqr", # or gesd
    alpha = 0.05
  ) %>% 
  time_recompose()

fifteen_min_anomalized %>%
  filter(g <= 10) %>%
  plot_anomalies(ncol = 3, alpha_dots = 0.25, time_recomposed = T)

fifteen_min_anomalized %>%
  filter(g > 10 & g <= 20) %>%
  plot_anomalies(ncol = 3, alpha_dots = 0.25, time_recomposed = T)

fifteen_min_anomalized %>%
  filter(g > 20 & g <= 30) %>%
  plot_anomalies(ncol = 3, alpha_dots = 0.25, time_recomposed = T)
