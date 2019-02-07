library(plyr)
library(dplyr)
library(skimr)
library(ez)

setwd("/Volumes/Mavericks/Users/ray/Workspace/Data_Analysis/SSAT_line")

file.list <- list.files(
  path = "pilot_data",
  pattern = 'txt',
  full.names = TRUE
)

dat <- ldply(
  file.list, function(file.name) {
    temp = read.csv(file.name, header = TRUE, sep = '\t', skip = 16)
  return(temp)
})

practice <- c(1:8)

dat <- dat %>% filter(!block_num %in% practice)

dat$set_size <- as.factor(dat$set_size)

dat_space <- dat %>% filter(search_type == "space")
dat_time <- dat %>% filter(search_type == "time")

space_rt <- subset(dat_space, present_absent == "present") %>%
  select(set_size, target_distractor, distractor_distractor, spatial_rt) %>%
  group_by(target_distractor, distractor_distractor) %>%
  summarise(meanRT = mean(spatial_rt))

ezPlot(
  data = subset(dat_space, present_absent == 'present')
  , wid = participant
  , dv = spatial_rt
  , within = .(set_size, target_distractor, distractor_distractor)
  , x = set_size
  , row = target_distractor
  , col = distractor_distractor
)

time_rt <- subset(dat_time, present_absent == "present") %>%
  select(target_distractor, distractor_distractor, temporal_rt) %>%
  group_by(target_distractor, distractor_distractor) %>%
  summarise(meanRT = mean(temporal_rt))

ezPlot(
  data = subset(dat_time, present_absent == 'present')
  , wid = participant
  , dv = temporal_rt
  , within = .(target_distractor, distractor_distractor)
  , x = set_size
  , row = target_distractor
  , col = distractor_distractor
)
