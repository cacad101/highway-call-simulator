""" Data generation Utility
- Uniform Distribution
- Uniform Distribution (Integer)
- Exponential Distribution
- Normal Distribution
"""

import logging
import os

import numpy as np
import pandas as pd

from utils_highway_call_simulator.utility import init_logger, load_settings, get_settings_path_from_arg, ensure_dir, get_now_str


class RandomDataGenerator:
    """ Data generator class """

    def __init__(self, distribution_settings):
        """ Initialization """
        logging.info("[{}] Initialize object".format(self.__class__.__name__))
        self.set_arrival_time_settings(distribution_settings.arrival_time)
        self.set_inter_arrival_time_settings(distribution_settings.inter_arrival_time)
        self.set_base_station_settings(distribution_settings.base_station)
        self.set_call_loc_offset_settings(distribution_settings.call_loc_offset)
        self.set_call_duration_settings(distribution_settings.call_duration)
        self.set_car_velocity_settings(distribution_settings.car_velocity)
        self.set_car_direction_settings(distribution_settings.car_direction)

        self.arrival_time = 0.0
        self.arrival_count = 1
        self.col = ['Arrival no','Arrival time (sec)','Base station (sec)', 'Call location offset (meter)','Call duration (sec)','Car velocity (m/s)','Car direction']
        self.arrival_events = pd.DataFrame(columns=self.col)

    def set_arrival_time_settings(self, settings):
        """ Set arrival_time settings """
        logging.info("[{}] Set arrival_time settings{}".format(self.__class__.__name__, settings))
        self.arrival_time_settings = settings

    def set_inter_arrival_time_settings(self, settings):
        """ Set inter_arrival_time settings """
        logging.info("[{}] Set inter_arrival_time settings{}".format(self.__class__.__name__, settings))
        self.inter_arrival_time_settings = settings

    def set_base_station_settings(self, settings):
        """ Set base_station settings """
        logging.info("[{}] Set base_station settings{}".format(self.__class__.__name__, settings))
        self.base_station_settings = settings

    def set_call_loc_offset_settings(self, settings):
        """ Set call_loc_offset settings """
        logging.info("[{}] Set call_loc_offset settings{}".format(self.__class__.__name__, settings))
        self.call_loc_offset_settings = settings

    def set_call_duration_settings(self, settings):
        """ Set call_duration settings """
        logging.info("[{}] Set call_duration settings{}".format(self.__class__.__name__, settings))
        self.call_duration_settings = settings

    def set_car_velocity_settings(self, settings):
        """ Set car_velocity settings """
        logging.info("[{}] Set car_velocity settings{}".format(self.__class__.__name__, settings))
        self.car_velocity_settings = settings

    def set_car_direction_settings(self, settings):
        """ Set car_direction settings """
        logging.info("[{}] Set car_direction settings{}".format(self.__class__.__name__, settings))
        self.car_direction_settings = settings

    def get_next(self, save=True):
        """ Get next random data """
        logging.debug("[{}] Generating random data, save={}".format(self.__class__.__name__, save))
        arrival_no = self.arrival_count
        arrival_time = self.arrival_time
        base_station = getattr(np.random, self.base_station_settings.dist)(*self.base_station_settings.set)
        call_loc_offset = getattr(np.random, self.call_loc_offset_settings.dist)(*self.call_loc_offset_settings.set)
        call_duration = getattr(np.random, self.call_duration_settings.dist)(*self.call_duration_settings.set)
        car_velocity = getattr(np.random, self.car_velocity_settings.dist)(*self.car_velocity_settings.set)
        car_direction = getattr(np.random, self.car_direction_settings.dist)(*self.car_direction_settings.set)

        arrival_event = [arrival_time, base_station, call_loc_offset, call_duration, car_velocity, car_direction]
        if save:
            arrival_frame = pd.DataFrame([[arrival_no]+arrival_event], columns=self.col)
            self.arrival_events = self.arrival_events.append(arrival_frame)

        inter_arrival_time = getattr(np.random, self.inter_arrival_time_settings.dist)(*self.inter_arrival_time_settings.set)
        self.arrival_time += inter_arrival_time
        self.arrival_count += 1
        logging.debug("[{}] Data generated={}".format(self.__class__.__name__, arrival_event))
        return arrival_event

    def save(self, path, ext=""):
        """ Save list of arrival events to file """
        logging.info("[{}] Saving list of arrival event to {}".format(self.__class__.__name__, path))
        ensure_dir(path)
        save_file = os.path.join(path, "arrival_event_"+str(ext)+".csv")
        self.arrival_events.to_csv(save_file, index = False)


def main():
    file_name = os.path.basename(__file__)[:-3]
    settings_path = get_settings_path_from_arg(file_name)
    settings = load_settings(settings_path)

    init_logger(settings.log.path, file_name, settings.log.level)
    logging.info("[{}] Logging initiated".format(file_name))

    dg = RandomDataGenerator(settings.simulator.distribution)
    for i in range(settings.simulator.event):
        dg.get_next()
    this_folder = os.path.join(settings.data.input_file, get_now_str())
    dg.save(this_folder)

if __name__ == "__main__":
    main()