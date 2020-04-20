library(readr)
library(tidyverse)
library(dplyr)

data <- read_csv("data/processed_dataset.csv") %>%   
  mutate(date_time = as.POSIXct(date_time, format="%d/%m/%Y %H:%M", tz="UTC")) %>% 
  mutate(
    site = as.factor(site),
    channel_id = as.factor(channel_id),
    date_time = as.POSIXct(date_time, format="%d/%m/%Y %H:%M", tz="UTC"),
    duplicate_date=F,
    mismatched_usages = 0
  )  

data_summary <- data %>%
    group_by(channel_id, site) %>% 
    arrange(date_time) %>%
    summarise(
      earliest = first(date_time) %>% format(format="%d/%m/%Y %H:%M", tz="UTC"),
      latest = last(date_time) %>% format(format="%d/%m/%Y %H:%M", tz="UTC"),
      dates_n = date_time %>% length(),
      unique_dates_n = date_time %>% unique() %>% length(),
      dupe_dates_n = dates_n - unique_dates_n
    ) 

data_duplicates <- data %>%
  group_by(channel_id) %>% 
  group_modify(~{
    data.frame(
      duped_date=duplicated(.x$date_time),
      date_time=.x$date_time,
      usage=.x$usage,
      site=.x$site
    )
  }) %>%
  filter(duped_date == T)

unique_date_duplicates <- data_duplicates$date_time %>% unique() 
unique_date_duplicates %>% length()

duplicate_summary <- data_duplicates %>%
  ungroup() %>%
  mutate(
    date_time = as.factor(date_time),
    channel_id = as.integer(channel_id)
  ) %>%
  group_by(date_time) %>%
  group_modify(~{
    data.frame(
      n_channel_dupes = .x$channel_id %>% unique() %>% length(),
      n_site_dupes = .x$site %>% unique() %>% length()
    )
  })

data_duplicated_values <- data %>%
  filter(date_time %in% unique_date_duplicates) %>% 
  ungroup() %>%
  group_by(channel_id, date_time) %>%
  mutate(
    duplicate_date=T,
    mismatched_usages = usage %>% 
      unique() %>% 
      length() -1
  ) %>% 
  arrange(channel_id, date_time) %>% 
  ungroup()

merged_data <- data_duplicated_values %>% 
  full_join(
    data %>% 
      filter(!date_time %in% unique_date_duplicates) 
  ) %>% 
  arrange(channel_id, date_time)
  