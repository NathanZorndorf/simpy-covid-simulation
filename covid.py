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
N_POPULATION = 10000 # total homes (or persons in v1)
P_INFECTION = 0.03 # pulled this number out of my bottom (this is what marble dude used)
CFR_USA = 0.017 # case fatality rate for USA as of Feb 2, 2021; see https://ourworldindata.org/mortality-risk-covid
SIM_TIME = 1000 # in days  
T_HOME = [1, 14] # in days
T_SICK = [14, 56]
T_QUARANTINE = 14 # in days 
D_SHOP = [10, 200] # in dollars

# global variables
people = []

# metrics
income = {}
cases = {}
deaths = {}
recoveries = {}

# setup Person object
class Person(object):
    def __init__(self, env, i):
        self.env = env
        self.id = i
        self.infected = 0
        self.immune = 0
        self.vaccinated = 0
        self.dead = 0 
        self.money_spent = 0

    def live(self):

        # the first day of their life, wait a random amount of time before doing anything
        days_at_home = random.randint(*T_HOME)
        yield self.env.timeout(days_at_home)

        while True:

            # if dead, do nothing
            if self.dead:
                while True:
                    yield self.env.timeout(1)

            # if not sick, go shopping
            if not self.infected:

                # calculate amount of money spent
                self.money_spent = random.randint(*D_SHOP)

                # if not immune, roll the dice on getting sick
                if not self.immune:
                    # probability of infection due to shopping is a constant
                    self.infected = random.binomial(1, p=P_INFECTION)

            # if they get infected at the store, then wait at home 14 days
            if self.infected:
                # if sick, spent time quarantined/in bed
                time_sick = random.randint(*T_SICK)
                yield self.env.timeout(time_sick) # quarantine in sickness

                # model chance of death
                self.dead = random.binomial(1, p=CFR_USA)
                if self.dead:
                    self.infected = 0
                    self.immune = 0

                # if they survive, then gain immunity
                if not self.dead:
                    self.infected = 0
                    self.immune = 1 # gain immunity after being sick and quarantining 
            else:
                # otherwise, wait at home a random amount of time
                days_at_home = random.randint(*T_HOME)
                yield self.env.timeout(days_at_home)

def collect_metrics(env, people):
    while True:
        income[env.now] = sum([person.money_spent for person in people])
        cases[env.now] = sum([person.infected for person in people])
        deaths[env.now] = sum([person.dead for person in people])
        recoveries[env.now] = sum([person.immune for person in people])

        # reset money spent by each person for this day
        for person in people:
            person.money_spent = 0

        # wait a day
        yield env.timeout(1)

# main
def main():

    # setup environment
    env = simpy.Environment()

    # create people
    people = [Person(env, i) for i in range(N_POPULATION)]

    # setup processes
    for person in people:
        env.process(person.live()) # initialize a process for each person
    env.process(collect_metrics(env, people)) # collect metrics at the end of each day
    
    # run simulation
    env.run(until=SIM_TIME)

    # export 
    df = pd.DataFrame({
        'income':pd.Series(income),
        'cases':pd.Series(cases),
        'deaths':pd.Series(deaths),
        'recoveries':pd.Series(recoveries),
    })
    filename = __file__.split('.')[0]
    df.to_csv(f'./out/{filename}.csv', index=True)

if __name__ == "__main__":
    main()