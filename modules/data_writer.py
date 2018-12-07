import os
import json
import shutil

from google.protobuf.json_format import MessageToJson, MessageToDict


def write_json_measurements(episode_path, data_point_id, measurements, control, control_noise,
                            state):

    with open(os.path.join(episode_path, 'measurements_' + data_point_id.zfill(5) + '.json'), 'w') as fo:

        jsonObj = MessageToDict(measurements)
        jsonObj.update(state)
        jsonObj.update({'steer': control.steer})
        jsonObj.update({'throttle': control.throttle})
        jsonObj.update({'brake': control.brake})
        jsonObj.update({'hand_brake': control.hand_brake})
        jsonObj.update({'reverse': control.reverse})
        jsonObj.update({'steer_noise': control_noise.steer})
        jsonObj.update({'throttle_noise': control_noise.throttle})
        jsonObj.update({'brake_noise': control_noise.brake})

        fo.write(json.dumps(jsonObj, sort_keys=True, indent=4))


def write_sensor_data(episode_path, data_point_id, sensor_data, sensors_frequency):
    try:
        from PIL import Image as PImage
    except ImportError:
        raise RuntimeError(
            'cannot import PIL, make sure pillow package is installed')

    for name, data in sensor_data.items():
        if int(data_point_id) % int((1/sensors_frequency[name])) == 0:
            format = '.png'
            if 'RGB' in name:
                format = '.png'
            if 'Lidar' in name:
                format = '.ply'
            data.save_to_disk(os.path.join(episode_path, name + '_' + data_point_id.zfill(5)), format)


def make_dataset_path(dataset_path):
    if not os.path.exists(dataset_path):
        os.makedirs(dataset_path)


def add_metadata(dataset_path, settings_module):
    with open(os.path.join(dataset_path, 'metadata.json'), 'w') as fo:
        jsonObj = {}
        jsonObj.update(settings_module.sensors_yaw)
        jsonObj.update({'fov': settings_module.FOV})
        jsonObj.update({'width': settings_module.WINDOW_WIDTH})
        jsonObj.update({'height': settings_module.WINDOW_HEIGHT})
        jsonObj.update({'lateral_noise_percentage': settings_module.lat_noise_percent})
        jsonObj.update({'longitudinal_noise_percentage': settings_module.long_noise_percent})
        jsonObj.update({'car range': settings_module.NumberOfVehicles})
        jsonObj.update({'pedestrian range': settings_module.NumberOfPedestrians})
        jsonObj.update({'set_of_weathers': settings_module.set_of_weathers})
        fo.write(json.dumps(jsonObj, sort_keys=True, indent=4))

def add_episode_metadata(dataset_path, episode_number, episode_aspects):

    if not os.path.exists(os.path.join(dataset_path, 'episode_' + episode_number)):
        os.mkdir(os.path.join(dataset_path, 'episode_' + episode_number))

    with open(os.path.join(dataset_path, 'episode_' + episode_number, 'metadata.json'), 'w') as fo:

        jsonObj = {}
        jsonObj.update({'number_of_pedestrian': episode_aspects['number_of_pedestrians']})
        jsonObj.update({'number_of_vehicles': episode_aspects['number_of_vehicles']})
        jsonObj.update({'seeds_pedestrians': episode_aspects['seeds_pedestrians']})
        jsonObj.update({'seeds_vehicles': episode_aspects['seeds_vehicles']})
        jsonObj.update({'weather': episode_aspects['weather']})
        fo.write(json.dumps(jsonObj, sort_keys=True, indent=4))



def add_data_point(measurements, control, control_noise, sensor_data, state,
                   dataset_path, episode_number, data_point_id, sensors_frequency):

    episode_path = os.path.join(dataset_path, 'episode_' + episode_number)
    if not os.path.exists(os.path.join(dataset_path, 'episode_' + episode_number)):
        os.mkdir(os.path.join(dataset_path, 'episode_' + episode_number))
    write_sensor_data(episode_path, data_point_id, sensor_data, sensors_frequency)
    write_json_measurements(episode_path, data_point_id, measurements, control, control_noise,
                            state)

# Delete an episode in the case
def delete_episode(dataset_path, episode_number):

    shutil.rmtree(os.path.join(dataset_path, 'episode_' + episode_number))