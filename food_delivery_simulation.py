"""
Food Delivery Dispatch System - Performance Simulation
Author: Prasadika
Date: October 2025
Case Study: Performance Modeling - Food Delivery Dispatch System
"""

import simpy
import random
import statistics
import matplotlib.pyplot as plt
import pandas as pd

# PARAMETERS
SIM_TIME = 180  # minutes 
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# ORDER PROCESS CLASS
class FoodDeliverySystem:
    def __init__(self, env, num_riders, delivery_time_mean, order_rate):
        self.env = env
        self.riders = simpy.Resource(env, num_riders)
        self.delivery_time_mean = delivery_time_mean
        self.order_rate = order_rate

        # Data tracking
        self.wait_times = []
        self.delivery_times = []
        self.busy_time = 0.0
        self.num_riders = num_riders

    def deliver_order(self, order_id):
        """Simulate the delivery process for an order."""
        # Delivery duration follows an exponential distribution
        delivery_duration = random.expovariate(1.0 / self.delivery_time_mean)
        yield self.env.timeout(delivery_duration)
        self.delivery_times.append(delivery_duration)

    def process_order(self, order_id):
        """Handle a single order: wait for a rider, then deliver."""
        arrival_time = self.env.now
        with self.riders.request() as request:
            yield request
            wait = self.env.now - arrival_time
            self.wait_times.append(wait)

            start = self.env.now
            yield self.env.process(self.deliver_order(order_id))
            end = self.env.now
            self.busy_time += (end - start)

    def generate_orders(self):
        """Generate orders using a Poisson process."""
        order_id = 0
        while True:
            interarrival = random.expovariate(self.order_rate)
            yield self.env.timeout(interarrival)
            order_id += 1
            self.env.process(self.process_order(order_id))

# SIMULATION RUNNER
def run_simulation(num_riders, order_rate, delivery_time_mean=15):
    """Run the simulation and return performance metrics."""
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    system = FoodDeliverySystem(env, num_riders, delivery_time_mean, order_rate)
    env.process(system.generate_orders())
    env.run(until=SIM_TIME)

    avg_wait = statistics.mean(system.wait_times) if system.wait_times else 0
    avg_delivery = statistics.mean(system.delivery_times) if system.delivery_times else 0
    utilization = (system.busy_time / (SIM_TIME * num_riders)) * 100
    orders_completed = len(system.delivery_times)

    return {
        "Riders": num_riders,
        "Order Rate": round(order_rate, 2),
        "Avg Wait Time (min)": round(avg_wait, 2),
        "Avg Delivery Time (min)": round(avg_delivery, 2),
        "Rider Utilization (%)": round(utilization, 2),
        "Orders Completed": orders_completed,
    }