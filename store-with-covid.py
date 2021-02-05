'''
Simple simulation in which N people randomly decide to take a trip to the grocery store each day.
'''

import os
import simpy
from numpy import random
import numpy as np
from scipy.interpolate import interp1d
import pandas as pd
import matplotlib.pyplot as plt

# set seed
random.seed(42)

# parameters
N_POPULATION = 1000 # total homes (or persons in v1)
N_ALLOWED = 1000
P_INFECTION = 0.03 # pulled this number out of my bottom (this is what marble dude used)
CFR_USA = 0.017 # case fatality rate for USA as of Feb 2, 2021; see https://ourworldindata.org/mortality-risk-covid
SIM_TIME = 60 # in days  
T_HOME = [1, 14] # in days
T_QUARANTINE = 14 # in days
D_SHOP = [10, 200] # in dollars

# global variables
people = []
num_positive = 0

# metrics
income = {}
cases = {}
deaths = {}
immunes = {}

# setup Person object
class Person(object):
    def __init__(self, env, i):
        self.env = env
        self.id = i
        self.infected = random.binomial(1, p=P_INFECTION) # have a chance to start out infected
        self.immune = 0
        self.dead = 0 

    def live(self, store):
        while True:
            # if dead, do nothing
            if self.dead:
                return

            # if not sick, go shopping
            if not self.infected:
                with store.request() as req:

                    # yield the request (lets other people in the store)
                    yield req

                    # calculate amount of money spent
                    # money_spent = interp1d(T_HOME,D_SHOP)(days_at_home) # just assume time = money
                    money_spent = random.randint(*D_SHOP)
                    income[self.env.now] += money_spent
                    # metrics[self.env.now]['income'] += money_spent

                    # chance of getting sick
                    if not self.immune:
                        # probability of infection due to shopping is a constant
                        self.infected = random.binomial(1, p=P_INFECTION)
                        # self.infected = 1
                        # self.infected = 0

                        # probability of infection scales with # of people inside store
                        # get # of people using resource currently 
                        # risk = store.count * P_INFECTION
                        # self.infected = random.binomial(1, p=risk)


                        # probability of infection scales with # of SICK people inside store
                        # I have no idea how to model the probability of exposure given # of people inside store at once...
                        # num_infected_shoppers = sum([person for person in people if (person.infected and person.shopping)])
                        # risk = num_infected_shoppers * P_INFECTION
                        # self.infected = random.binomial(1, p=risk)
                        

            # if they get infected at the store, then wait at home 14 days
            if self.infected:
                # model chance of death
                self.dead = random.binomial(1, p=CFR_USA)
                if self.dead:
                    self.infected = 0
                    self.immune = 0
                    return
                if not self.dead:
                    yield self.env.timeout(T_QUARANTINE) # quarantine
                    self.infected = 0
                    self.immune = 1 # gain immunity after being sick and quarantining 
            else:
                # otherwise, wait at home a random amount of time in interval T_HOME
                days_at_home = random.randint(*T_HOME)
                yield self.env.timeout(days_at_home)

# run simulation top level function
def run_simulation(env, people, store):
    # initialize a process for each person
    for person in people:
        env.process(person.live(store))

    while True:
        # import ipdb; ipdb.set_trace();
        # income gets reset daily
        income[env.now] = 0

        # count the cases of covid cases after everyone goes shopping
        cases[env.now] = sum([person.infected for person in people])
        deaths[env.now] = sum([person.dead for person in people])
        immunes[env.now] = sum([person.immune for person in people])

        # sleep 
        yield env.timeout(1) # wait a day (everyone goes home and sleeps)
        

# main
def main():

    # setup environment
    env = simpy.Environment()

    # setup grocery store
    store = simpy.Resource(env, N_ALLOWED)

    # create people
    people = [Person(env, i) for i in range(N_POPULATION)]

    # run simulation
    env.process(run_simulation(env, people, store))
    
    # run simulation
    env.run(until=SIM_TIME)

    # export 
    df = pd.DataFrame({
        'income':pd.Series(income),
        'cases':pd.Series(cases),
        'deaths':pd.Series(deaths),
        'immunes':pd.Series(immunes),
    })
    filename = __file__.split('.')[0]
    df.to_csv(f'./out/{filename}.csv', index=True)

if __name__ == "__main__":
    main()