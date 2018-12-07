#!/usr/bin/env python
import sys
import json
import numpy as np
import glob
import re
import scipy
import shutil
import argparse
from PIL import Image
import matplotlib.pyplot as plt
import math

import time
import os
from collections import deque
import seaborn as sns

sns.set(color_codes=True)


from modules.screen_manager import ScreenManager


class Control:
    steer = 0
    throttle = 0
    brake = 0
    hand_brake = 0
    reverse = 0


# Configurations for this script


sensors = {'RGB': 3, 'labels': 3, 'depth': 0}
resolution = [800, 600]
#camera_id_position = 25
#direction_position = 24
#speed_position = 10
#number_of_seg_classes = 5
classes_join = {0: 2, 1: 2, 2: 2, 3: 2, 5: 2, 12: 2, 9: 2, 11: 2, 4: 0, 10: 1, 8: 3, 6: 3, 7: 4}


def join_classes(labels_image, join_dic):
    compressed_labels_image = np.copy(labels_image)
    for key, value in join_dic.iteritems():
        compressed_labels_image[np.where(labels_image == key)] = value

    return compressed_labels_image


def join_classes_for(labels_image, join_dic):
    compressed_labels_image = np.copy(labels_image)
    # print compressed_labels_image.shape
    for i in range(labels_image.shape[0]):
        for j in range(labels_image.shape[1]):
            compressed_labels_image[i, j, 0] = join_dic[labels_image[i, j, 0]]

    return compressed_labels_image
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

    parser.add_argument(
        '-c', '--check_dataset',
        action='store_true',
        help='flag to set if the dataset is checked'
    )
    parser.add_argument(
        '-s', '--step_size',
        type=int,
        default = 1
    )

    args = parser.parse_args()
    path = args.path

    # By setting episodes as all, it means that all episodes should be visualized
    if args.episodes == 'all':
        episodes_list = glob.glob(os.path.join(path, 'episode_*'))
        sort_nicely(episodes_list)
    else:
        episodes_list = args.episodes

    data_configuration_name = 'coil_training_dataset'
    print ( data_configuration_name)
    print ('dataset_configurations.' + (data_configuration_name) )
    settings_module = __import__('dataset_configurations.' + (data_configuration_name),
                                 fromlist=['dataset_configurations'] )




    first_time = True
    count = 0
    steering_pred = []
    steering_gt = []
    step_size = args.step_size
    # initial_positions =[20,25,48,68,79,105,108,120,130]
    # positions_to_test = []
    # for i in initial_positions:
    #  positions_to_test += range(i-1,i+2)


    screen = ScreenManager()

    image_queue = deque()

    actions_queue = deque()

    # Start a screen to show everything. The way we work is that we do IMAGES x Sensor.
    # But maybe a more arbitrary configuration may be useful

    screen.start_screen([resolution[0], resolution[1]], [3, 1], 1)
    ts = []



    steer_gt_order = [0] * 3
    steer_pred1_order = [0] * 3
    steer_pred2_order = [0] * 3

    steer_pred1_vec = []
    steer_pred2_vec = []
    steer_gt_vec = []

    actions = [Control()] * sensors['RGB']
    actions_noise = [Control()] * sensors['RGB']

    steer_vec = []
    throttle_vec = []
    brake_vec = []
    steer_noise_vec = []
    throttle_noise_vec = []
    brake_noise_vec = []
    speed_vec = []


    try:

        for episode in episodes_list[-1:]:
            print ('Episode ', episode)
            if 'episode' not in episode:
                episode = 'episode_' + episode

            # Take all the measurements from a list
            measurements_list = glob.glob(os.path.join(episode, 'measurement*'))
            sort_nicely(measurements_list)


            if args.check_dataset:
                # This part of the dataset was already checked. CONTINUE
                if os.path.exists(os.path.join(episode, "checked")) or os.path.exists(os.path.join(episode, "bad_episode")):
                    continue


            print (measurements_list)

            for i in range(0, len(measurements_list)-1, step_size):
                measurement = measurements_list[i]
                data_point_number = measurement.split('_')[-1].split('.')[0]
                print (data_point_number)

                with open(measurement) as f:
                    measurement_data = json.load(f)

                rgb_center_name = 'CentralRGB_' + data_point_number.zfill(5) + '.png'
                rgb_left_name = 'LeftRGB_' + data_point_number + '.png'
                rgb_right_name ='RightRGB_' + data_point_number + '.png'

                rgb_center = scipy.ndimage.imread(os.path.join(episode, rgb_center_name))
                rgb_left = scipy.ndimage.imread(os.path.join(episode, rgb_left_name))
                rgb_right = scipy.ndimage.imread(os.path.join(episode, rgb_right_name))

                if 'forwardSpeed' in  measurement_data['playerMeasurements']:
                    speed = measurement_data['playerMeasurements']['forwardSpeed']
                else:
                    speed = 0


                steer_vec.append(measurement_data['steer'])
                throttle_vec.append(measurement_data['throttle'])
                brake_vec.append(measurement_data['brake'])
                steer_noise_vec.append(measurement_data['steer_noise'])
                throttle_noise_vec.append(measurement_data['throttle_noise'])
                brake_noise_vec.append(measurement_data['brake_noise'])
                speed_vec.append(speed)
                status = {}

                status.update(
                    {
                        'directions': measurement_data['directions'],
                        "stop_pedestrian": measurement_data['stop_pedestrian'],
                        "stop_traffic_lights": measurement_data['stop_traffic_lights'],
                        "stop_vehicle": measurement_data['stop_vehicle']


                    }
                )


                screen.plot_camera_steer(rgb_left, [measurement_data['steer'], measurement_data['throttle'], measurement_data['brake']], [0, 0])
                screen.plot_camera_steer(rgb_center, [measurement_data['steer'], measurement_data['throttle'], measurement_data['brake']],
                                         [1, 0], status=status)
                screen.plot_camera_steer(rgb_right, [measurement_data['steer'], measurement_data['throttle'], measurement_data['brake']], [2, 0])


                print (speed)

                if  measurement_data['steer'] != measurement_data['steer_noise']:
                    print ("LATERAL NOISE")

                if  measurement_data['throttle'] != measurement_data['throttle_noise']:
                    print ("LONGITUDINAL NOISE")
                #figure_plot(steer_pred1_vec, steer_pred2_vec, steer_gt_vec, count)
                count += 1


            if args.check_dataset:
                answer = ''
                while answer != 'y' and answer != 'n' and answer != 'd' :
                    answer = input('Was the episode good ? ')

                    if answer == 'y':
                        done_file = open(os.path.join(episode, "checked"), 'w')
                        done_file.close()
                    elif answer == 'd':
                        shutil.rmtree(episode)
                    else:
                        done_file = open(os.path.join(episode, "bad_episode"), 'w')
                        done_file.close()




    except KeyboardInterrupt:
        x = range(len(steer_vec))

        dif_steer = [math.fabs(x - y) for x, y in zip(brake_vec, brake_noise_vec)]

        # We plot the noise addition for steering
        plt.plot(x, dif_steer, 'r', x, steer_vec, 'g', x, steer_noise_vec, 'b')
        plt.show()

        # We plot the speed plus brake and throttle x 10

        brake10 = [x*10 for x in brake_noise_vec]

        throttle10 = [x*10 for x in throttle_noise_vec]

        plt.plot(x, brake10, 'r', x, throttle10, 'g', x, speed_vec, 'b')
        plt.show()


    # save_gta_surface(gta_surface)
