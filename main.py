""" Main File """

import logging
import os

import numpy as np

from highway_call_simulator import HighwayCallSimulator
from utils_highway_call_simulator.data_generator import RandomDataGenerator
from utils_highway_call_simulator.utility import init_logger, load_settings, get_settings_path_from_arg, get_now_str
from utils_highway_call_simulator.visualisation import visualize_line, visualize_histogram

def main():
    file_name = os.path.basename(__file__)[:-3]
    settings_path = get_settings_path_from_arg(file_name)
    settings = load_settings(settings_path)

    init_logger(settings.log.path, "all_"+file_name, settings.log.level)
    logging.info("[{}] Logging initiated".format(file_name))

    reserved_channel = settings.simulator.variable.reserved_channel
    base_count = settings.simulator.variable.base_count
    base_diameter = settings.simulator.variable.base_diameter
    base_channel = settings.simulator.variable.base_channel
    image_stat_path = os.path.join(settings.data.image_file, "highway_simulator_test")

    for i in range(base_channel):
        blocked_call = []
        dropped_call = []
        for _ in range(settings.simulator.simulation_count):
            simulator = HighwayCallSimulator(i, base_count, base_diameter, base_channel)
            data_generator = RandomDataGenerator(settings.simulator.distribution)
            blocked, dropped = simulator.simulate(settings.simulator.event, data_generator, settings.simulator.warm_up_threshold)
            blocked_call.append(blocked)
            dropped_call.append(dropped)
            visualize_line(simulator.dropped_call_history, "dropped_call", image_stat_path)
            visualize_line(simulator.blocked_call_history, "blocked_call", image_stat_path)
            input_path = os.path.join(settings.data.input_file, "highway_simulator_test")
            data_generator.save(input_path, ext=get_now_str())

        logging.warning("Reserved: {}".format(i))
        print("Blocked: {0:.3f}".format(np.mean(blocked_call*100)))
        logging.warning("Blocked: {}".format(np.mean(blocked_call*100)))
        print("Dropped: {0:.3f}".format(np.mean(dropped_call*100)))
        logging.warning("Dropped: {}".format(np.mean(dropped_call*100)))


if __name__ == "__main__":
    main()
