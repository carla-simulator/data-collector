#!/usr/bin/env python

import glob
import re


import argparse

import os
from collections import deque



class Control:
    steer = 0
    throttle = 0
    brake = 0
    hand_brake = 0
    reverse = 0


# Configurations for this script


sensors = {'RGB': 3, 'labels': 3, 'depth': 0}
resolution = [800, 600]

classes_join = {0: 2, 1: 2, 2: 2, 3: 2, 5: 2, 12: 2, 9: 2, 11: 2, 4: 0, 10: 1, 8: 3, 6: 3, 7: 4}


def tryint(s):
    try:
        return int(s)
    except:
        return s

def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [tryint(c) for c in re.split('([0-9]+)', s) ]

def sort_nicely(l):
    """ Sort the given list in the way that humans expect.
    """
    l.sort(key=alphanum_key)

# ***** main loop *****
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Path viewer')
    # parser.add_argument('model', type=str, help='Path to model definition json. Model weights should be on the same path.')
    parser.add_argument('-pt', '--path', default="")

    parser.add_argument(
        '--episodes',
        nargs='+',
        dest='episodes',
        type=str,
        default ='all'
    )

    args = parser.parse_args()
    path = args.path

    # By setting episodes as all, it means that all episodes should be visualized
    if args.episodes == 'all':
        episodes_list = glob.glob(os.path.join(path, 'episode_*'))
    else:
        episodes_list = args.episodes



    first_time = True
    count = 0
    steering_pred = []
    steering_gt = []
    step_size = 1
    # initial_positions =[20,25,48,68,79,105,108,120,130]
    # positions_to_test = []
    # for i in initial_positions:
    #  positions_to_test += range(i-1,i+2)



    # Start a screen to show everything. The way we work is that we do IMAGES x Sensor.
    # But maybe a more arbitrary configuration may be useful

    ts = []

    total_number_of_seconds = 0
    total_number_of_checked_seconds = 0
    total_number_of_bad_seconds = 0


    for episode in episodes_list:
        print ('Episode ', episode)
        if 'episode' not in episode:
            episode = 'episode_' + episode

        # Take all the measurements from a list
        measurements_list = glob.glob(os.path.join(episode, 'measurement*'))
        sort_nicely(measurements_list)

        if len (measurements_list) > 0:

            print (measurements_list[-1])
            data_point_number = measurements_list[-1].split('_')[-1].split('.')[0]

            total_number_of_seconds += float(data_point_number)/10.0


            if os.path.exists(os.path.join(episode, "bad")):
                total_number_of_bad_seconds += float(data_point_number)/10.0

            if os.path.exists(os.path.join(episode, "processed2")):
                total_number_of_checked_seconds += float(data_point_number)/10.0



    print( 'Total Hours = ',  total_number_of_seconds/3600.0)

    print( 'Total Hours Valid = ',  total_number_of_checked_seconds/3600.0)

    print( 'Total Hours BAD = ',  total_number_of_bad_seconds/3600.0)

    # save_gta_surface(gta_surface)
