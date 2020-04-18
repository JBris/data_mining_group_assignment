library(readr)
library(tidyverse)
library(dplyr)

data <- read_csv("data/processed_dataset.csv")

project_summary <- function(col) {
  summary <- data %>%
    group_by(!!col) %>% 
    mutate(date_time = as.POSIXct(date_time, format="%d/%m/%Y %H:%M", tz="UTC")) %>%
    arrange(date_time) %>%
    summarise(
      mean = mean(usage), 
      median = median(usage), 
      n = n(), 
      sd = sd(usage),
      IQR = IQR(usage),
      min = min(usage),
      max = max(usage),
      earliest_date = first(date_time) %>% format("%d/%m/%Y %H:%M"),
      latest_date = last(date_time) %>% format("%d/%m/%Y %H:%M")
    )
  summary
}

channel_id_summary <- project_summary(data$channel_id)
site_summary <-project_summary(data$site)
