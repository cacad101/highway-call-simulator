""" Script to detect distribution settings """

import os
import logging

import numpy as np
import pandas as pd
import scipy.stats as sc

from utils_highway_call_simulator.utility import init_logger, load_settings, get_settings_path_from_arg, get_now_str
from utils_highway_call_simulator.visualisation import visualize_histogram


def main():
    file_name = os.path.basename(__file__)[:-3]
    settings_path = get_settings_path_from_arg(file_name)
    settings = load_settings(settings_path)

    init_logger(settings.log.path, file_name, settings.log.level)
    logging.info("[{}] Logging initiated".format(file_name))

    logging.info("[{}] Input data loaded from {}".format(file_name, settings.data.real_input))
    real_input = pd.read_csv(settings.data.real_input)

    save_to =  os.path.join(settings.data.image_file, get_now_str())
    plot = True
    bins = 20
    size = 10000

    # Arrival Time
    col = "Arrival time (sec)"
    logging.info("[{}] Detecting distribution for {}".format(file_name, col))
    data = real_input[col]
    min_val = data.to_frame().min()
    max_val = data.to_frame().max()
    logging.info("[{}] Uniform disctribution with min:{}, max:{}".format(file_name, min_val, max_val))
    new_data = np.random.uniform(low=min_val, high=max_val, size=size)
    new_min_val = data.to_frame().min()
    new_max_val = data.to_frame().max()
    logging.info("[{}] Uniform disctribution with min:{}, max:{}".format(file_name, new_min_val, new_max_val))
    visualize_histogram(new_data, "generated_"+"_".join(col.split()[:-1]), save_to=save_to, plot=plot, bins=bins)
    logging.info("[{}] Visualizing data data:{}, save_to:{}, plot:{}".format(
        file_name, col, save_to, plot
        ))

    # Inter-arrival Time
    col = "Inter arrival time (sec)"
    logging.info("[{}] Detecting distribution for {}".format(file_name, col))
    data = data.diff()
    data.drop(0, inplace=True)
    _, scale = sc.expon.fit(data)
    logging.info("[{}] Exponential disctribution with scale:{}".format(file_name, scale))
    new_data = np.random.exponential(scale=scale, size=size)
    _, new_scale = sc.expon.fit(data)
    logging.info("[{}] Exponential disctribution with scale:{}".format(file_name, new_scale))
    visualize_histogram(new_data, "generated_"+"_".join(col.split()[:-1]), save_to=save_to, plot=plot, bins=bins)
    logging.info("[{}] Visualizing data data:{}, save_to:{}, plot:{}".format(
        file_name, col, save_to, plot
        ))

    # Base Station
    col = "Base station (sec)"
    logging.info("[{}] Detecting distribution for {}".format(file_name, col))
    data = real_input[col]
    min_val = int(data.to_frame().min())
    max_val = int(data.to_frame().max())
    logging.info("[{}] Uniform disctribution with min:{}, max:{}".format(file_name, min_val, max_val))
    new_data = np.random.randint(low=min_val, high=max_val, size=size)
    new_min_val = int(data.to_frame().min())
    new_max_val = int(data.to_frame().max())
    logging.info("[{}] Uniform disctribution with min:{}, max:{}".format(file_name, new_min_val, new_max_val))
    visualize_histogram(new_data, "generated_"+"_".join(col.split()[:-1]), save_to=save_to, plot=plot, bins=bins)
    logging.info("[{}] Visualizing data data:{}, save_to:{}, plot:{}".format(
        file_name, col, save_to, plot
        ))

    # Call Duratoin
    col = "Call duration (sec)"
    logging.info("[{}] Detecting distribution for {}".format(file_name, col))
    data = real_input[col]
    _, scale = sc.expon.fit(data)
    logging.info("[{}] Exponential disctribution with scale:{}".format(file_name, scale))
    new_data = np.random.exponential(scale=scale, size=size)
    _, new_scale = sc.expon.fit(data)
    logging.info("[{}] Exponential disctribution with scale:{}".format(file_name, new_scale))
    visualize_histogram(new_data, "generated_"+"_".join(col.split()[:-1]), save_to=save_to, plot=plot, bins=bins)
    logging.info("[{}] Visualizing data data:{}, save_to:{}, plot:{}".format(
        file_name, col, save_to, plot
        ))

    # Velocity
    col = "velocity (km/h)"
    logging.info("[{}] Detecting distribution for {}".format(file_name, col))
    data = real_input[col]
    data = (data * 10)/36
    mean = np.mean(data)
    std = np.std(data)
    logging.info("[{}] Normal disctribution with mean:{}, std:{}".format(file_name, mean, std))
    new_data = np.random.normal(loc=mean, scale=std, size=size)
    new_mean = np.mean(new_data)
    new_std = np.std(new_data)
    logging.info("[{}] Sample generated normal disctribution with mean:{}, std:{}".format(file_name, new_mean, new_std))
    visualize_histogram(new_data, "generated_"+"_".join(col.split()[:-1]), save_to=save_to, plot=plot, bins=bins)
    logging.info("[{}] Visualizing data data:{}, save_to:{}, plot:{}".format(
        file_name, col, save_to, plot
        ))


if __name__ == "__main__":
    main()