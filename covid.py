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


import simpy
from numpy import random
import numpy as np
from scipy.interpolate import interp1d

# set seed
random.seed(42)

# parameters
N_POPULATION = 100 # total homes (or persons in v1)
P_TRANSMISSION = 0.001 # p_transmission = probability of infecting someone else while inside 
P_INIT = 0.001 # p_init = initial proportion of people that are infected
N_ALLOWED = 30
SIM_TIME = 60 # in days  
T_HOME = [1*24*60, 14*24*60]
T_SHOP = [10, 60]
RECOVERY_TIME = [7*24*60, 14*24*60]

# global variables
population = np.zeros(N_POPULATION)
people = []

# metrics
income = []
infections = []


class Person(object):
    def __init__(self, env, person_id):
        self.env = env
        self.person_id = person_id
        self.infected = random.binomial(1, p=P_INIT)
        self.recovery_time = random.randint(*RECOVERY_TIME)
        self.recovered = 0 
        self.time_infected = 0
        
        # count infected person
        population[self.person_id] = self.infected
    
    def shop(self, grocery_store):
        # if person has not recovered, then don't go shopping
        if (self.env.now() - self.time_infected) < self.recovery_time:
            pass
        else:
            with grocery_store.request() as req:
                yield req

                # shop
                shopping_time = random.randint(*T_SHOP)
                yield self.env.process(self.env.timeout(shopping_time))

                # calculate amount of money spent
                money_spent = interp1d(T_SHOP,T_SHOP)(shopping_time) # just assume time = money
                income.append((self.env.now(), money_spent))

                # calculate risk of infection
                # depending on how many people are in the store
                # how many are sick
                # and probability of transmission
                shoppers = grocery_store.users
                num_infected_shoppers = sum([shopper.infected for shopper in shoppers])
                risk = num_infected_shoppers * P_TRANSMISSION
                exposed = random.binomial(1, p=risk) # determine if exposed

                # determine new state 
                if self.recovered:
                    self.infected = 0   
                    population[self.person_id] = 0

                if self.infected == 0 and exposed:
                    self.time_infected = self.env.now()
                    self.infected = 1
                    population[self.person_id] = 1

    def go_home(self):
        # calculate proportion of population that is infected
        # I don't know where to put this, so here it goes
        p = sum(population) / len(population)
        infections.append((self.env.now(), p))

        # wait at home a random time amount
        # mean wait time of 1 week = 10,080 minutes
        yield self.env.timeout(random.randint(*T_HOME))

    def live_life(self, grocery_store):
        self.shop(grocery_store)
        self.go_home()

def run_simulation(env, people, grocery_store):
    while True:
        for person in people:
            env.process(person.live_life(grocery_store))
        # yield env.timeout() # 

def main():

    # setup environment
    env = simpy.Environment()

    # setup grocery store
    grocery_store = simpy.Resource(env, N_ALLOWED)

    # create people
    people = [Person(env, i) for i in range(N_POPULATION)]

    # run simulation
    env.process(run_simulation(env, people, grocery_store))

    # for i in range(N_POPULATION):
    #     person = Person(env, 'person_%d' % i)
    #     # env.process(person.live_life(grocery_store))
    #     people.append()
    #     env.process(run_simulation(env, 'person_%d' % i, grocery_store))
    
    # run simulation
    env.run(until=SIM_TIME * 24 * 60)



if __name__ == "__main__":
    main()