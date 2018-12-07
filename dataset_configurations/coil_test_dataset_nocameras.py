import random


import numpy as np
from carla import sensor
from carla.settings import CarlaSettings

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600



POSITIONS = [[19, 66], [79, 14], [19, 57], [39, 53], [60, 26],
             [53, 76], [42, 13], [31, 71], [59, 35], [47, 16],
             [10, 61], [66, 3], [20, 79], [14, 56], [26, 69],
             [79, 19], [2, 29], [16, 14], [5, 57], [77, 68],
             [70, 73], [46, 67], [57, 50], [61, 49], [21, 12]
             ]
# [27, 12] [43, 54], [33, 5], [56, 65] [23, 1] [54, 30] [51, 81],


#TODO for now all the resolutions and FOVs are the same.
FOV = 100



sensors_frequency = {'CameraRGB': 1}


# TODO: automatically read this from the sensors
sensors_yaw = {'CameraRGB': 0}


lat_noise_percent = 100

long_noise_percent = 0



set_of_weathers = [1, 3, 6, 8]


NumberOfVehicles = [30, 30] #[20, 45]  # The range for the random numbers that are going to be generated
NumberOfPedestrians = [40, 40] #[35, 80] #[




def make_carla_settings():
    """Make a CarlaSettings object with the settings we need."""



    settings = CarlaSettings()
    settings.set(
        SendNonPlayerAgentsInfo=True,
        SynchronousMode=True,
        NumberOfVehicles=30,
        NumberOfPedestrians=50,
        WeatherId=1)

    settings.set(DisableTwoWheeledVehicles=True)

    settings.randomize_seeds() # IMPORTANT TO RANDOMIZE THE SEEDS EVERY TIME
    camera0 = sensor.Camera('CameraRGB')
    camera0.set_image_size(WINDOW_WIDTH, WINDOW_HEIGHT)
    camera0.set(FOV=100)
    camera0.set_image_size(800, 600)
    camera0.set_position(2.0, 0.0, 1.4)
    camera0.set_rotation(-15.0, 0, 0)

    settings.add_sensor(camera0)

    return settings




# 65, 18 to 65, 16

# 18, 145 to 16, 145

# 79, 45 to 79 47