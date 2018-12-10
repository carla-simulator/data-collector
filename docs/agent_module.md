Expert Demonstrator
================

 The expert has access to privileged information
about the simulation state, including the exact map of the
environment and the exact positions of the ego-car, all other
vehicles, and pedestrians.




#### Local/Global Planner

The expert navigation has the following characteristics.

* The path driven by the expert is calculated using a planner
* This planner uses an A* algorithm to determine the path to reach a certain
goal.
* This path is then converted into waypoints.
* A  PID controller generates the throttle, brake, and steering based
on the waypoints.
* The expert drives on the center of the lane.
* The expert keeps a constant speed of 35 km/h when driving straight and reduces the
speed when making turns to about 15 km/h.




#### Obstacle Avoidance

The agent has the following obstacle avoidance behaviours:

* Reduce speed for pedestrians that are from 5 to 15 meters away
* Completely stop for pedestrians closer than 5 meters away.
* Follows lead vehicle, imitating the lead vehicle speed.
* Stop for red traffic lights.

To compute all the obstacle avoidance behaviors the position and
 orientation of the ego-car on the map are used. The position
 of all the other objects; vehicles, pedestrians and traffic lights;
  are also used.


#### Noiser

To improve diversity, realism, and increase the number of
visited state-action pairs, we add noise to the ego car controls.
 This reduces the difference between offline training and
 online testing scenarios.
 The noise simulates a gradual drift away from the desired
 trajectory of the expert. However, for training,
 the drift is not used as signal to imitate, only the reactions performed
 by the expert. The noiser class can be seen [here](../modules/noiser.py)

