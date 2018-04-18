""" Script to visualise data from csv """

import os
import logging

import numpy as np
import pandas as pd

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

    save_to = os.path.join(settings.data.image_file, get_now_str())
    plot = False
    bins = 20
    for col in real_input.columns:
        logging.info("[{}] Visualizing data data:{}, save_to:{}, plot:{}".format(
            file_name, col, save_to, plot
            ))
        visualize_histogram(real_input[col], "_".join(col.split()[:-1]), save_to=save_to, plot=plot, bins=bins)

    arrival_time = real_input["Arrival time (sec)"]
    inter_arrival_time = arrival_time.diff()
    inter_arrival_time.drop(0,inplace=True)
    visualize_histogram(inter_arrival_time, "inter_arrival", save_to=save_to, plot=plot, bins=bins)



if __name__ == "__main__":
    main()