library(readr)
library(tidyverse)
library(dplyr)

data <- read_csv("data/processed_dataset.csv") %>%   
  mutate(date_time = as.POSIXct(date_time, format="%d/%m/%Y %H:%M", tz="UTC")) %>% 
  mutate(
    site = as.factor(site),
    channel_id = as.factor(channel_id),
    date_time = as.POSIXct(date_time, format="%d/%m/%Y %H:%M", tz="UTC"),
    missing=F
  )  

data_padded <- data %>% 
  group_by(channel_id, site) %>% 
  group_modify(~{
    date_range <- seq.POSIXt(
      from = first(.x$date_time),
      to = last(.x$date_time),
      by = "15 mins"
    )
    df=data.frame(
      date_time=date_range
    )
    full_join(df, .x) %>% return()
  }) %>% 
  mutate(
    missing=is.na(missing)
  ) %>% 
  arrange(site, channel_id, date_time)

data_padded_summary <- data_padded %>%
  group_by(channel_id) %>% 
  arrange(date_time) %>%
  summarise(
    earliest = first(date_time) %>% format(format="%d/%m/%Y %H:%M", tz="UTC"),
    latest = last(date_time) %>% format(format="%d/%m/%Y %H:%M", tz="UTC"),
    dates = date_time %>% length(),
    unique_dates = date_time %>% unique() %>% length(),
    dupe_dates = dates - unique_dates
  )
    
missing_observations <- data_padded %>% 
  filter(missing == T) %>%
  arrange(channel_id, date_time)

missing_observation_count <- missing_observations %>% 
  group_by(channel_id, site) %>%
  summarise(
    duplicate_dates = unique(date_time) %>% length()
  )
