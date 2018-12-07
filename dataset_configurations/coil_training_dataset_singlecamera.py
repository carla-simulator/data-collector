from carla import sensor
from carla.settings import CarlaSettings
"""
Example of dataset configuration. See a more complex example at coil_training_dataset.py
"""
# The image size definition for the cameras
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

#Positions a vector of tuples containing the [START, END] positions
#of the episodes that the (expert driver)[docs/agent_module.md] is going to follow. The
#possible positions for agent placement can be viewed by running
POSITIONS = [[71, 127], [21, 116],  [51, 49], [35, 110], [91, 85],
             [93, 114], [7, 30], [133, 110], [43, 60], [98, 11], [49, 96], [85, 90],
             [40, 27], [74, 37], [41, 97], [62, 110], [2, 19], [114, 138], [76, 131],
             [95, 116], [71, 50], [97, 15], [74, 71], [133, 50],
             [116, 23], [116, 38], [52, 101], [108, 5], [79, 23], [68, 13]]
# The FOV for all the cameras
FOV = 100
# The frequency where all the the camera will be colleted. 1 means every frame, 0.5 every two frames
sensors_frequency = {'CameraRGB': 1}
# The yaw of every sensor.
sensors_yaw = {'CameraRGB': 0}
# The percentage of episodes to have lateral noise. More information about the noise can
# be found at docs/agent_module.md
lat_noise_percent = 0
# The percentage of episodes with longitudinal noise.
long_noise_percent = 0
# The interval of vehicles/pedestrians that every episode can have
NumberOfVehicles = [30, 60]  # The range for the random numbers that are going to be generated
NumberOfPedestrians = [50, 100]

set_of_weathers = [1, 3, 6, 8]

"""
Returns the entire CarlaSettings to be used on all the episodes.
Here we are defining the cameras used. The number of vehicles and pedestrians will 
be sampled from the interval defined on the NumberOfVehicle and NumberOfPedestrians variables.
This function must be redefined on each of the daset cofiguration files.
"""

def make_carla_settings():
    """Make a CarlaSettings object with the settings we need."""

    settings = CarlaSettings()
    settings.set(
        SendNonPlayerAgentsInfo=True,
        SynchronousMode=True)
    settings.set(DisableTwoWheeledVehicles=True)

    settings.randomize_seeds()
    # Add a carla camera.
    camera0 = sensor.Camera('CameraRGB')
    camera0.set_image_size(WINDOW_WIDTH, WINDOW_HEIGHT)
    camera0.set(FOV=FOV)
    camera0.set_position(2.0, 0.0, 1.4)
    camera0.set_rotation(-15.0, 0, 0)
    settings.add_sensor(camera0)

    return settings

