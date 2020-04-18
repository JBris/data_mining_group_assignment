library(readr)
library(tidyverse)
library(dplyr)

data <- read_csv("data/processed_dataset.csv")

project_summary <- function(col) {
  summary <- data %>%
    group_by(!!col) %>% 
    summarise(
      mean = mean(usage), 
      median = median(usage), 
      n = n(), 
      sd = sd(usage),
      IQR = IQR(usage),
      min = min(usage),
      max = max(usage)
    )
  summary
}

channel_id_summary <- project_summary(data$channel_id)
site_summary <-project_summary(data$site)
