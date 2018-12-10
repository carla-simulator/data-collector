Dataset Format
==============

This library colects a driving datasets using a hardcoded expert driver navigating towards a goal.

The module used to write the dataset can be seen [here](../modules/data_writer.py)

##### General Structure

A dataset directory should look like the structure below. In the next sections
will explain each of one the components described.

```
<dataset_name>
│   dataset_metadata.json
│
└───episode_00000
│   │   episode_metadata.json
│   │   <Camera1_name>_00000.png
│   │   ...
│   │   <Camera2_name>_00000.png
│   │   ...
│   │   <Lidar_name>_00000.png
│   │   ...
│   │   measurements_00000.json
│   │   ...
└───episode_00001
    │   ...
    │
    ...
```


###### Dataset metadata

Each dataset contains a metadata file with the following
information:

* Cameras used.
* The FOV, and image size for the cameras.
* The range of the number of cars to be used in each episode.
* The range of the number of pedestrians to be used in each episode.
* The percentage of [lateral noise](agent_module.md/#noiser).
* The percentage of longitudinal noise.
* The set of weathers to be sampled from.



###### Episode Metadata


Each episode is stored on a different folder.
For each collected episode we generate a json file containing
its general aspects that are:

* Number of Pedestrians: the total number of spawned pedestrians.
* Number of Vehicles: the total number of spawned vehicles.
* Spawned seed for pedestrians and vehicles: the random seed used for
    the CARLA object spawning process.
* Weather: the weather of the episode.

Each episode lasts from 1-5 minutes
partitioned in simulation steps of 100 ms.
For each step, we store data divided
into two different categories, sensor dat
stored as PNG images, and measurement data stored as json files.

###### Sensor Data

All images collected are stored as png.
All lidar sensors collected are store as PLY files.
The collected sensors are the ones described in
the [configuration file](../dataset_configurations/coil_training_dataset_singlecamera.py).


##### Measurements

Measurements represent all the float data collected for each simulation
step. Each measurement is associated with the respective sensor data.
The units of the measurements are on SI format, otherwise we specify
the format.
All measurements are stored in json files and contain the
following information:

* Step Number: the number of the current simulation step, starts at zero and is incremented by one for every simulation step.
* Game Timestamp: the time that has passed since the simulation has started. Expressed on miliseconds.
* Position: the world position of the ego-vehicle. It is expressed as a three dimensional vector (x,y,z) in meters.
* Orientation: the orientation of the vehicle with respect
    to the world. Expressed as Euler angles (row, pitch and yaw).
* Acceleration: the acceleration vector of the ego-vehicle
    with respect to the world.
* Forward Speed: an scalar expressing the linear forward
    speed of the vehicle.
* Intentions: a signal that is proportional to the effect that the dynamic objects on the scene are having on the ego car actions. We use three different intention signals: stopping for pedestrians, stopping for cars and stopping for traffic lights. For example, an intention of 1 for stopping for pedestrian means that the ego car is totally stopped for a pedestrians that is less than 5 meters away. An intention of the same class of 0.5 means that the expert noticed a pedestrians and has reduced its speed to a certain extent. An intention of 0 means there are no pedestrians nearby in the field of view of the expert.

* High Level Commands: the high level command saying what the ego-vehicle should do in the next intersection: go straight, turn left, turn right, or do not care (the ego vehicle
    could pick any option). These commands are encoded as an
    integer number. 2 is do not care, 3 for turn left, 4 for turn right, 5 for go straight.
* Waypoints: a set containing the 10 future positions of the vehicle.
* Steering Angle: the current angle of the vehicle's steering wheel. Normalized from -1 to 1
* Throttle: the current pressure on the throttle pedal. Normalized
from 0 to 1.
* Brake: the current pressure on the brake pedal.Normalized
from 0 to 1.
* Hand Brake: if the hand brake is activated.
* Steer Noise: the current steering angle in the vehicle considering the noise function.
* Throttle Noise: the current pressure on the throttle pedal considering the noise function.
* Brake Noise: the current pressure on the brake pedal considering the noise function. The noise function is described [here](agent_module.md/#noiser).

For each one of the non-player agents (pedestrians, vehicles,
traffic light), the following information is provided:

* Unique ID: an unique identifier of this agent.
* Type: if it is a pedestrian, a vehicle or a traffic light.
* Position: the world position of the agent. It is expressed as a three dimensional vector (x,y,z)  in meters.
* Orientation: the orientation of the agent with respect
    to the world. Expressed as Euler angles (row, pitch and yaw).
* Forward Speed: an scalar expressing the linear forward
    speed of the agent.
* State: only for traffic lights, contains the state of the traffic light, if it is either red, yellow or green.

