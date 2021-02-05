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
N_POPULATION = 2 # total homes (or persons in v1)
N_ALLOWED = 1000
P_INFECTION = 0.03 # pulled this number out of my bottom (this is what marble dude used)
CFR_USA = 0.017 # case fatality rate for USA as of Feb 2, 2021; see https://ourworldindata.org/mortality-risk-covid
SIM_TIME = 120 # in days  
T_HOME = [1, 14] # in days
T_QUARANTINE = 14 # in days 
D_SHOP = [10, 200] # in dollars

# global variables
people = []

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
        # self.infected = random.binomial(1, p=P_INFECTION) # have a chance to start out infected
        self.infected = 0 # have a chance to start out infected
        self.immune = 0
        self.dead = 0 
        self.money_spent = 0

    def live(self, store):
        while True:
            import ipdb; ipdb.set_trace();
            # if dead, do nothing
            if self.dead:
                yield

            print('Person {} arrives at store at time {}'.format(self.id,self.env.now))
            # if not sick, go shopping
            if not self.infected:

                # calculate amount of money spent
                self.money_spent = random.randint(*D_SHOP)
                # income[self.env.now] += money_spent

                # if not immune, roll the dice on getting sick
                if not self.immune:
                    # probability of infection due to shopping is a constant
                    # self.infected = random.binomial(1, p=P_INFECTION)
                    self.infected = 0


            # if they get infected at the store, then wait at home 14 days
            if self.infected:
                # wait a random amount of time

                # model chance of death
                self.dead = random.binomial(1, p=CFR_USA)
                if self.dead:
                    self.infected = 0
                    self.immune = 0
                    yield
                if not self.dead:
                    yield self.env.timeout(T_QUARANTINE) # quarantine
                    print('Person {} ends quarantine at time {}'.format(self.id,self.env.now))
                    self.infected = 0
                    self.immune = 1 # gain immunity after being sick and quarantining 
            else:
                # otherwise, wait at home a random amount of time in interval T_HOME
                days_at_home = random.randint(*T_HOME)
                yield self.env.timeout(days_at_home)
                print('Person {} needs to go shopping at time {}'.format(self.id,self.env.now))

# callback for resetting income of story each day
# def reset_income(event):
#     import ipdb; ipdb.set_trace();
#     print('income gets reset for day {}'.format(event.value+1))
#     income[event.value+1] = 0

# run simulation top level function
def run_simulation(env, people, store):

    # initialize a process for each person
    for person in people:
        env.process(person.live(store))

    # initialize income
    income[env.now] = 0

    while True:
        import ipdb; ipdb.set_trace();
        # sleep 
        yield env.timeout(1) # wait a day (everyone goes home and sleeps)

        import ipdb; ipdb.set_trace();
        # count the cases of covid cases after everyone goes shopping
        income[env.now-1] = sum([person.money_spent for person in people])
        cases[env.now-1] = sum([person.infected for person in people])
        deaths[env.now-1] = sum([person.dead for person in people])
        immunes[env.now-1] = sum([person.immune for person in people])

        # reset people's money spent at the end of the day
        for person in people:
            person.money_spent = 0 
        

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