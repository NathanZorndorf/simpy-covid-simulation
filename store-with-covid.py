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
N_POPULATION = 100 # total homes (or persons in v1)
N_ALLOWED = 30
P_INFECTION = 0.001
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


# setup Person object
class Person(object):
    def __init__(self, env):
        self.env = env
        self.infected = random.binomial(1, p=P_INFECTION) # have a chance to start out infected
        self.immune = 0

    def shop(self, store):

        # if not sick, go shopping
        if not self.infected:
            with store.request() as req:
                yield req

                # calculate amount of money spent
                # money_spent = interp1d(T_HOME,D_SHOP)(days_at_home) # just assume time = money
                money_spent = random.randint(*D_SHOP)
                income[self.env.now] += money_spent
                # metrics[self.env.now]['income'] += money_spent

                # chance of getting sick
                if not self.immune:
                    self.infected = random.binomial(1, p=P_INFECTION)

        # if they get infected at the store, then wait at home 14 days
        if self.infected:
            # num_positive += 1 # add to case count
            yield self.env.timeout(T_QUARANTINE) # quarantine
            # num_positive -= 1 # subtract from case count once healed
            self.infected = 0
            self.immune = 1 # gain immunity after being sick 
        else:
            # otherwise, wait at home a random amount of time in interval T_HOME
            days_at_home = random.randint(*T_HOME)
            yield self.env.timeout(days_at_home)

# run simulation top level function
def run_simulation(env, people, store):
    while True:
        # income gets reset daily
        income[env.now] = 0

        # every person runs shopping routine daily
        for person in people:
            env.process(person.shop(store))

        # count the cases of covid cases after everyone goes shopping
        cases[env.now] = sum([person.infected for person in people])

        # sleep 
        yield env.timeout(1) # wait a day (everyone goes home and sleeps)
        

# main
def main():

    # setup environment
    env = simpy.Environment()

    # setup grocery store
    store = simpy.Resource(env, N_ALLOWED)

    # create people
    people = [Person(env) for _ in range(N_POPULATION)]

    # run simulation
    env.process(run_simulation(env, people, store))
    
    # run simulation
    env.run(until=SIM_TIME)

    # export 
    df = pd.DataFrame({
        'income':pd.Series(income),
        'cases':pd.Series(cases),
    })
    filename = __file__.split('.')[0]
    df.to_csv(f'./out/{filename}.csv', index=True)

if __name__ == "__main__":
    main()