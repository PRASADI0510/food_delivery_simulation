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


# MAIN EXECUTION: TEST SCENARIOS
def main():
    print("=== Food Delivery Dispatch System Simulation ===\n")

    scenarios = {
        "A - Base Case": {"riders": 5, "order_rate": 0.6},    # Normal operation
        "B - More Riders": {"riders": 8, "order_rate": 0.6},  # Increased resources
        "C - High Demand": {"riders": 5, "order_rate": 1.2},  # High demand
    }

    results = {}

    for name, params in scenarios.items():
        print(f"Running Scenario {name}...")
        metrics = run_simulation(
            num_riders=params["riders"],
            order_rate=params["order_rate"],
        )
        results[name] = metrics

    # Display Results Summary
    print("\n--- Simulation Results Summary ---")
    for name, data in results.items():
        print(f"\n{name}")
        for k, v in data.items():
            print(f"{k:25}: {v}")

    # Visualization
    labels = list(results.keys())
    wait_times = [results[k]["Avg Wait Time (min)"] for k in labels]
    utilization = [results[k]["Rider Utilization (%)"] for k in labels]
    delivery_times = [results[k]["Avg Delivery Time (min)"] for k in labels]

    # Bar chart - Average Wait Time
    plt.figure(figsize=(8, 5))
    plt.bar(labels, wait_times, color='skyblue')
    plt.title("Average Wait Time by Scenario")
    plt.xlabel("Scenario")
    plt.ylabel("Average Wait Time (minutes)")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()

    # Line chart - Rider Utilization
    plt.figure(figsize=(8, 5))
    plt.plot(labels, utilization, marker='o', color='green')
    plt.title("Rider Utilization Comparison")
    plt.xlabel("Scenario")
    plt.ylabel("Rider Utilization (%)")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()

    # Bar chart - Average Delivery Time
    plt.figure(figsize=(8, 5))
    plt.bar(labels, delivery_times, color='orange')
    plt.title("Average Delivery Time by Scenario")
    plt.xlabel("Scenario")
    plt.ylabel("Average Delivery Time (minutes)")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()
    
    df = pd.DataFrame(results).T
    df.to_csv("simulation_results.csv")



if __name__ == "__main__":
    main()
