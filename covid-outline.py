# S = number of susceptible persons
# I = number of infected persons
# R = number of recovered persons (unable to be re-infected)
# (V = number of vaccinated persons (unable to be infected) - for v2)

## Target (measurement) variables
# p = proportion of people that are infected 
# d = dollars that the grocery store makes

## Global (i.e. community) variables 
# n_homes = number of homes in the community ( = number of people for v1)
# p_init = initial proportion of people that are infected

## Grocery store predictor variables
# n_allowed = number of people allowed inside at once
# p_transmission = probability of infecting someone else while inside 

## Home predictor variables
# n = number of residents (1 for v1, uniform/binomial/other distribution random variable for v2)
# (r = transmissability ratio inside home OR probability of infecting someone else while inside)

# Q: what's the chances of getting covid-19 at safeway for a random person in manor?
    # (depending on how much time I spend inside)
    # depending on how many people are inside
        # depending on the status of the people inside
        # depending on how many people are let in at one time
    # whether they are wearing a mask or not

# Q: How many people should be allowed inside the grocery store at once?

# process
    # every few days (determined by binomial random variable), person takes trip to grocery store
        # while in the grocery store, they have a probability of coming into contact
        # with every other person inside the store

# assumptions
    # this community only has single-occupancy residencies
    # people just stay at home except when they go to the grocery store
    # there is only one grocery store for the entire community 
    # the grocery store is open 24 hours a day
    # the amount of money a person spends on a grocery trip is ~ to the time they spend inside the store
