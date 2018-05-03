""" Data visualisation Utility """

import os

import matplotlib.pyplot as plt

from utils_highway_call_simulator.utility import ensure_dir, get_now_str


def visualize_histogram(data, title, save_to="", plot=False, bins='auto'):
    """ Visualise data as histogram, optional 'plot' and 'save_to' args """
    plt.hist(data, bins=bins)
    plt.title(title)
    plt.xlabel("Value")
    plt.ylabel("Frequency")
    if save_to:
        ensure_dir(save_to)
        file_name = os.path.join(save_to, get_now_str()+"_"+title+".png")
        plt.savefig(file_name)
    if plot:
        plt.show()
    plt.close()

def visualize_line(data, title, save_to="", plot=False):
    """ Visualise data as simple line, optional 'plo' and 'save_to' args """
    plt.plot(data)
    plt.ylabel(title)
    if save_to:
        ensure_dir(save_to)
        file_name = os.path.join(save_to, get_now_str()+"_"+title+".png")
        plt.savefig(file_name)
    if plot:
        plt.show()
    plt.close()