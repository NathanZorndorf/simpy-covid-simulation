import simpy

def car(env):
    while True:
        print('Start parking at %d' % env.now)
        yield env.timeout(5) # park duation
        
        print('Start parking at %d' % env.now)
        yield env.timeout(2) # drive duration

env = simpy.Environment()
env.process(car(env))
env.run(until=15)