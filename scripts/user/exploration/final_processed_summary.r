library(readr)
library(tidyverse)
library(dplyr)

data <- read_csv("data/final_processed.csv") %>%   
  mutate(date_time = as.POSIXct(date_time, format="%d/%m/%Y %H:%M", tz="UTC")) %>% 
  mutate(
    site = as.factor(site),
    channel_id = as.factor(channel_id),
    date_time = as.POSIXct(date_time, format="%d/%m/%Y %H:%M", tz="UTC"),
  )  

data_summary <- data %>%
  group_by(channel_id, site) %>% 
  arrange(date_time) %>%
  group_modify(~{
    data.frame(
      earliest = first(.x$date_time) %>% format(format="%d/%m/%Y %H:%M", tz="UTC"),
      latest = last(.x$date_time) %>% format(format="%d/%m/%Y %H:%M", tz="UTC"),
      dates_n = .x$date_time %>% length(),
      unique_dates_n = .x$date_time %>% unique() %>% length(),
      dupe_dates_n = .x$date_time %>% length() - .x$date_time %>% unique() %>% length(),
      num_missing = .x$missing[.x$missing == 1] %>% length()
    )
  })
