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
SIM_TIME = 60 # in days  
T_HOME = [1, 14]
D_SHOP = [10, 200]

# global variables
people = []

# metrics
# income = np.zeros(SIM_TIME)
income = {}

# setup Person object
class Person(object):
    def __init__(self, env):
        self.env = env

    def shop(self, store):

        # after waiting, go shopping
        with store.request() as req:
            yield req

            # calculate amount of money spent
            # money_spent = interp1d(T_HOME,D_SHOP)(days_at_home) # just assume time = money
            money_spent = random.randint(*D_SHOP)
            income[self.env.now] += money_spent
        
        # wait at home a random amount of time in interval T_HOME
        days_at_home = random.randint(*T_HOME)
        yield self.env.timeout(days_at_home)

# run simulation top level function
def run_simulation(env, people, store):
    while True:
        income[env.now] = 0 # reset gross income to 0 on a daily basis
        for person in people:
            env.process(person.shop(store))
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
    df = pd.DataFrame.from_dict(income, orient='index', columns=['income'])
    filename = __file__.split('.')[0]
    df.to_csv(f'./out/{filename}.csv', index=True)

if __name__ == "__main__":
    main()