from datetime import datetime
import numpy as np

from scipy.stats import truncnorm

def datetime_to_seconds(time_str):
    time_data = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    seconds = time_data.hour * 3600 + time_data.minute * 60 + time_data.second
    return seconds
def time_to_seconds(time_str):
    time_format = "%H:%M:%S"
    time_object = datetime.strptime(time_str, time_format)

    total_seconds = time_object.hour * 3600 + time_object.minute * 60 + time_object.second
    return total_seconds
def seconds_to_time(seconds):
    time_object = datetime.utcfromtimestamp(seconds)
    return time_object.strftime("%H:%M:%S")

def truncated_normal_numpy(a, b, mean, std_dev):
    samples = np.random.normal(loc=mean, scale=std_dev)
    while not (a < samples < b):
        samples = np.random.normal(loc=mean, scale=std_dev)
    return samples

from scipy.stats import truncnorm

def truncated_normal_scipy(a, b, mean, std_dev):
    a, b = (a - mean) / std_dev, (b - mean) / std_dev
    samples = truncnorm.rvs(a, b, loc=mean, scale=std_dev)
    return samples

def read_walking_time(file_path,line_number):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            desired_line = file.readlines()[line_number - 1].split(",")
            return(int(desired_line[0]))
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except IndexError:
        print(f"Line {line_number} is out of range.")
from numba import jit

@jit(nopython=True)
def truncated_normal_numba(lower,upper,mu,sigma,size=1):
    """Generate truncated normal distribution samples."""
    samples = np.zeros(size)
    count = 0
    while count < size:
        x = np.random.normal(mu, sigma)
        if lower <= x <= upper:
            samples[count] = x
            count += 1
    return samples