""" Main simulation handler """

import logging
import os
import queue

from utils_highway_call_simulator.utility import init_logger, load_settings, get_settings_path_from_arg, get_now_str
from utils_highway_call_simulator.data_generator import RandomDataGenerator


class HighwayCallSimulator:
    """ High way call simulator main class """
    CALL_INITIATION_EVENT = "call_initiation"
    CALL_TERMINATION_EVENT = "call_termination"
    CALL_HANDOVER_EVENT = "call_handover"

    LEFT_DIRECTION = 0
    RIGHT_DIRECTION = 1

    def __init__(self, reserved_channel, base_count, base_diameter, base_channel):
        """ Initialization """
        logging.info("[{}] Initialize object".format(self.__class__.__name__))
        # Variables
        self.simulation_time = 0.0
        self.base_channel = base_channel
        self.base_count = base_count
        self.base = [base_channel for i in range(base_count)]
        self.base_diameter = base_diameter
        self.reserved_channel = reserved_channel

        # Stats
        self.get_stat = True
        self.total_call = 0
        self.total_dropped_call = 0
        self.total_blocked_call = 0

        # Events
        self.warm_up_threshold = False
        self.data_generator = None
        self.event_count = 0
        self.event_total_count = 0
        self.event_queue = queue.PriorityQueue()

    def schedule_event(self, event_type, event):
        """ Add new event to the queue """
        logging.debug("[{}] Scheduling {} event, with detail:{}".format(self.__class__.__name__, event_type, event))
        event.append(event_type)
        self.event_queue.put(event)

    def get_next_event(self):
        """ Get new event from the queue """
        logging.debug("[{}] Getting next event".format(self.__class__.__name__))
        if self.event_queue.empty():
            logging.debug("[{}] Failed to get new event, empty event_queue!".format(self.__class__.__name__))
            return False
        event = self.event_queue.get()
        logging.debug("[{}] Get next event: {}".format(self.__class__.__name__, event))
        return event

    def get_next_station(self, base_station, call_loc_offset, call_duration, car_velocity, car_direction):
        """ Get the next base station of the call """
        next_station = base_station
        remaining_distance = 0

        if car_direction == HighwayCallSimulator.LEFT_DIRECTION:
            # Left directed call
            next_station -= 1
            if call_loc_offset < 0:
                call_loc_offset = self.base_diameter
            remaining_distance = call_loc_offset
        else:
            # Right directed call
            next_station += 1
            if next_station >= self.base_count:
                next_station = -1
            if call_loc_offset < 0:
                call_loc_offset = 0
            remaining_distance = self.base_diameter - call_loc_offset

        current_duration = remaining_distance/car_velocity
        if current_duration >= call_duration:
            current_duration = call_duration
            next_station = -1
        return next_station, current_duration

    def get_previous_station(self, base_station, car_direction):
        """ Get the previous base station of the call """
        if car_direction == HighwayCallSimulator.LEFT_DIRECTION:
            return base_station + 1
        else:
            return base_station - 1

    def handle_initiation_call(self, base_station, call_loc_offset, call_duration, car_velocity, car_direction):
        """ Handling initiation call """
        logging.debug("[{}] Initiating call event, base_station:{}, call_loc_offset:{}, call_duration:{}, car_velocity:{}, car_direction:{}".format(
            self.__class__.__name__, base_station, call_loc_offset, call_duration, car_velocity, car_direction))
        # Schedule next initiation call event
        if self.event_total_count < self.event_count:
            next_initiation_event = self.data_generator.get_next()
            self.schedule_event(HighwayCallSimulator.CALL_INITIATION_EVENT, next_initiation_event)
            self.event_total_count += 1

        # Update total call
        if self.get_stat:
            self.total_call += 1

        if self.base[base_station] > self.reserved_channel:
            # Channel available
            self.base[base_station] -= 1
            next_station, current_duration = self.get_next_station(base_station, call_loc_offset, call_duration, car_velocity, car_direction)
            if next_station < 0:
                # Call terminated
                termination_time = self.simulation_time + current_duration
                termination_event = [termination_time, base_station]
                self.schedule_event(HighwayCallSimulator.CALL_TERMINATION_EVENT, termination_event)
            else:
                # Call handover
                handover_time = self.simulation_time + current_duration
                remaining_duration = call_duration - current_duration
                handover_event = [handover_time, next_station, remaining_duration, car_velocity, car_direction]
                self.schedule_event(HighwayCallSimulator.CALL_HANDOVER_EVENT, handover_event)
        else:
            # No channel available, call blocked
            if self.get_stat:
                self.total_blocked_call += 1

    def handle_termination_call(self, base_station):
        """ Handling termination call """
        logging.debug("[{}] Terminating call event, base_station:{}".format(self.__class__.__name__, base_station))
        self.base[base_station] += 1

    def handle_handover_call(self, base_station, call_duration, car_velocity, car_direction):
        """ Handling handover call """
        logging.debug("[{}] Handovering call event, base_station:{}, call_duration:{}, car_velocity:{}, car_direction:{}".format(
            self.__class__.__name__, base_station, call_duration, car_velocity, car_direction))
        # Free up previous channel
        prev_station = self.get_previous_station(base_station, car_direction)
        self.base[prev_station] += 1

        if self.base[base_station] > 0:
            # Channel available
            self.base[base_station] -= 1
            next_station, current_duration = self.get_next_station(base_station, -1, call_duration, car_velocity, car_direction)
            if next_station < 0:
                # Call terminated
                termination_time = self.simulation_time + current_duration
                termination_event = [termination_time, base_station]
                self.schedule_event(HighwayCallSimulator.CALL_TERMINATION_EVENT, termination_event)
            else:
                # Call handover
                handover_time = self.simulation_time + current_duration
                remaining_duration = call_duration - current_duration
                handover_event = [handover_time, next_station, remaining_duration, car_velocity, car_direction]
                self.schedule_event(HighwayCallSimulator.CALL_HANDOVER_EVENT, handover_event)
        else:
            # No channel available, call dropped
            if self.get_stat:
                self.total_dropped_call += 1


    def simulate(self, event_count, data_generator, warm_up_threshold=False):
        """ Start simulation """
        logging.info("[{}] Starting simulation, event_count:{}, data_generator:{}, warm_up_threshold:{}".format(
            self.__class__.__name__, event_count, data_generator.__class__.__name__, warm_up_threshold))
        self.event_count = event_count
        self.data_generator = data_generator
        self.warm_up_threshold = warm_up_threshold
        if warm_up_threshold:
            self.get_stat = False

        if self.event_total_count < self.event_count:
            next_initiation_event = self.data_generator.get_next()
            self.schedule_event(HighwayCallSimulator.CALL_INITIATION_EVENT, next_initiation_event)
            self.event_total_count += 1

        next_event = self.get_next_event()
        while next_event:
            if self.warm_up_threshold <= self.simulation_time:
                self.get_stat = True
            self.simulation_time = next_event[0]
            next_event_type = next_event[-1]
            if next_event_type == HighwayCallSimulator.CALL_INITIATION_EVENT:
                self.handle_initiation_call(*next_event[1:-1])
            elif next_event_type == HighwayCallSimulator.CALL_TERMINATION_EVENT:
                self.handle_termination_call(*next_event[1:-1])
            elif next_event_type == HighwayCallSimulator.CALL_HANDOVER_EVENT:
                self.handle_handover_call(*next_event[1:-1])
            next_event = self.get_next_event()

        return self.print_stats()

    def print_stats(self):
        """ Show stats report """
        logging.debug("[{}] Printing simulation stats".format(self.__class__.__name__))
        dropped_call = self.total_dropped_call/self.total_call
        blocked_call = self.total_blocked_call/self.total_call

        print("Blocked call: {}/{} ({}%)".format(self.total_blocked_call, self.total_call, blocked_call*100))
        logging.info("[{}] Blocked call: {}/{} ({}%)".format(
            self.__class__.__name__, self.total_blocked_call, self.total_call, blocked_call*100))
        print("Dropped call: {}/{} ({}%)".format(self.total_dropped_call, self.total_call, dropped_call*100))
        logging.info("[{}] Dropped call: {}/{} ({}%)".format(
            self.__class__.__name__, self.total_dropped_call, self.total_call, dropped_call*100))

        return blocked_call, dropped_call


def main():
    file_name = os.path.basename(__file__)[:-3]
    settings_path = get_settings_path_from_arg(file_name)
    settings = load_settings(settings_path)

    init_logger(settings.log.path, file_name, settings.log.level)
    logging.info("[{}] Logging initiated".format(file_name))

    reserved_channel = settings.simulator.variable.reserved_channel
    base_count = settings.simulator.variable.base_count
    base_diameter = settings.simulator.variable.base_diameter
    base_channel = settings.simulator.variable.base_channel

    simulator = HighwayCallSimulator(reserved_channel, base_count, base_diameter, base_channel)

    data_generator = RandomDataGenerator(settings.simulator.distribution)
    simulator.simulate(settings.simulator.event, data_generator, settings.simulator.warm_up_threshold)
    input_path = os.path.join(settings.data.input_file, "highway_simulator_test")
    data_generator.save(input_path, ext=get_now_str())

if __name__ == "__main__":
    main()

