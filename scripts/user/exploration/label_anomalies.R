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
  arrange(date_time)

fifteen_min_anomalized <- data %>%
  group_by(channel_id) %>%
  time_decompose(
    usage, 
    frequency = "1 day", 
    trend = "14 days", 
    method="twitter", # or stl
    merge = TRUE
  ) %>%
  anomalize(
    remainder, 
    method="iqr", # or gesd
    alpha = 0.05
  ) %>% 
  time_recompose()

fifteen_min_anomalized %>%
  mutate(
    anomaly = ifelse(anomaly== "Yes", 1, 0)
  ) %>%
  select(channel_id, date_time, usage, site, missing, month, day, hour, minute, anomaly) %>%
  write_csv("data/labelled_final_processed.csv")
