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
