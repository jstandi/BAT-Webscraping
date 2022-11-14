library(plm)
library(tidyverse)
library(estimatr)
library(ggalt)
library(wooldridge)
library(GGally)
library(sandwich)
library(lmtest)
library(mosaic)
library(broom)
library(car)
library(patchwork)

# reading in data, cleaning a bit
raw_auctions <- read_csv('bat_auction_data.csv')
auctions <- raw_auctions %>% filter(year_sold >= 20)
nine_six_four <- auctions %>% filter(model_year >= 1990) %>% filter(model_year <= 1994)

# basic stats to get a sense of the data
inspect(auctions)
ggpairs(auctions)
auctions %>% filter(!is_special) %>% inspect()
auctions %>% filter(!is_special) %>% filter(is_manual) %>% inspect()
auctions %>% filter(!is_special) %>% select(price_sold, model_year, mileage, body_type, is_manual) %>% ggpairs()
auctions %>% filter(is_special) %>% inspect()
auctions %>% filter(is_special) %>% select(price_sold, model_year, mileage, is_manual) %>% ggpairs()
inspect(nine_six_four)
ggpairs(nine_six_four)
nine_six_four %>% filter(!is_special) %>% ggpairs()

# messing around with models
regular_auctions <- auctions %>% filter(!is_special) %>% select(price_sold, model_year, mileage, body_type, is_manual, year_sold)
model1 <- lm(log(price_sold)~model_year + model_year + body_type + is_manual, data = regular_auctions)
summary(model1)
coeftest(model1, vcov = vcovHC, type = "HC1")

mileage_model <- lm(log(price_sold)~log(mileage), data = regular_auctions)
summary(mileage_model)
coeftest(mileage_model, vcov = vcovHC, type = "HC1")

regular_auctions %>% inspect()
adj_mileage_model <- plm(log(price_sold)~log(mileage), data = regular_auctions, index = c("year_sold"), method = "within", effect = "twoways")
summary(adj_mileage_model)
coeftest(adj_mileage_model, vcov = vcovHC, type = "HC1")

special_auctions <- auctions %>% filter(is_special) %>% select(price_sold, model_year, mileage, body_type, is_manual)
smodel1 <- lm(price_sold~model_year + is_manual, data = special_auctions)
summary(smodel1)
coeftest(smodel1, vcov = vcovHC, type = "HC1")

spec_mileage <- lm(log(price_sold)~log(mileage), data = special_auctions)
summary(spec_mileage)
coeftest(spec_mileage, vcov = vcovHC, type = "HC1")

cleaned <- nine_six_four %>% filter(!is.na(year_sold)) %>% filter(!is.na(body_type)) %>% filter(!is.na(is_manual)) %>% filter(!is.na(mileage))
six_four_model <- plm(log(price_sold)~log(mileage), data = cleaned, index = c("is_manual"), method = "within", effect = "twoways")
summary(six_four_model)
coeftest(six_four_model, vcov = vcovHC, type = "HC1")

# creating decent-looking graphs
auctions %>% filter(!is_special) %>% ggplot(aes(x = mileage, y = price_sold, color = model_year)) + geom_point(position = "jitter", alpha = .75) + geom_smooth() + 
  scale_x_continuous(name = "Mileage", breaks = c(0, 25000, 50000, 100000, 150000, 200000), labels = c("0 miles", "25,000", "50,000", "100,000", "150,000", "200,000")) + 
  scale_y_continuous(name = "Price Sold", limits = c(0, 300000), breaks = c(0, 50000, 100000, 200000, 300000), labels = c("$0", "$50,000", "$100,000", "$200,000", "$300,000")) + 
  scale_color_continuous(name = "Model Year") + 
  labs(title = "Porsche 911s Sold on bringatrailer.com in 2022") + 
  theme(panel.background = element_rect(fill = "white")) + 
  theme(panel.grid.major = element_line(color = "dark grey")) + 
  theme(axis.ticks = element_blank)

auctions %>% filter(!is_special) %>% ggplot(aes(x = mileage, y = price_sold, color = model_year)) + geom_point(position = "jitter", alpha = .9) + geom_smooth() + 
  scale_x_continuous(name = "Mileage", breaks = c(0, 25000, 50000, 100000, 150000, 200000), labels = c("0 miles", "25,000", "50,000", "100,000", "150,000", "200,000")) + 
  scale_y_continuous(name = "Price Sold", limits = c(0, 300000), breaks = c(0, 50000, 100000, 200000, 300000), labels = c("$0", "$50,000", "$100,000", "$200,000", "$300,000")) + 
  labs(title = "Porsche 911s Sold on bringatrailer.com from 2020-2022") + 
  theme(panel.background = element_rect(fill = "white")) + 
  theme(panel.grid.major = element_line(color = "dark grey")) + 
  theme(axis.ticks = element_blank())

# some leftover test graphs
auctions %>% filter(!is_special) %>% ggplot(aes(x = mileage, y = price_sold, color = is_manual)) + geom_point(alpha = .5) + geom_smooth()

auctions %>% filter(model_year == 1991) %>% filter(body_type == "Targa") %>% ggplot(aes(x = mileage, y = price_sold)) + geom_point() + geom_smooth()
regular_auctions %>% filter(model_year >= 1990) %>% filter(model_year <= 1994) %>% filter(body_type == "Targa") %>% inspect()