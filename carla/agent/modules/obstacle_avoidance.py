import math

from .utils import get_vec_dist, get_angle
from ...planner.map import CarlaMap


class ObstacleAvoidance(object):

    def __init__(self, param, city_name):

        self._map = CarlaMap(city_name)
        self.param = param

    """
        *************
        MAIN FUNCTION
        *************
    """

    def stop_for_agents(self, location, orientation, wp_angle, wp_vector, agents):
        """
        Function to determine if the ego-agent is going to be stop for dynamic obstacles.
        A  semi-circle  is computed on the direction of the ego-car orientation.
        The semi-circle size is proportional to the distance the ego-car
        is set to react to. These settings are set on the self.param at the class
        initialization. If this semi circle interesects
        with an object, the ego-car reacts to it, by stopping or
        reducing its speed.
        Args:
            location: The location of the ego vehicle
            orientation: orientation of the ego vehicle
            wp_angle: The angle with the active waypoint
            wp_vector: the vector with the waypoint vector
            agents: the transforms of all the agents, positions orientations. The agents
                    are traffic ligths, vehicles and pedestrians.

        Returns:
            speed_factor: A speed factor saying how much the ego-vehicle should slow down
            state: A dictionary containing the state of all the other agents and how much
                   each class of agent is contributing for the speed reduction of the
                   ego-vehicle.
        """



        # Start the speed factor for each possible dynamic factor. Multiple agents
        # can contribute to reduce the target speed of the agent
        speed_factor = 1
        speed_factor_tl = 1
        speed_factor_p = 1
        speed_factor_v = 1
        active_agents_ids = []  # The list of pedestrians that are on roads or nearly on roads

        for agent in agents:
            if agent.HasField('traffic_light') and self.param['stop4TL']:
                if self.is_traffic_light_active(location, agent,
                                                orientation) and self.is_traffic_light_visible(
                                                                 location, agent):
                    speed_factor_tl = self.stop_traffic_light(location, agent, wp_vector,
                                                              wp_angle, speed_factor_tl)

                    if agent.traffic_light.state != 0:
                        active_agents_ids.append(agent.id)

            if agent.HasField('pedestrian') and self.param['stop4P']:
                if self.is_pedestrian_hitable(agent.pedestrian):
                    speed_factor_p = self.stop_pedestrian(location, agent, wp_vector,
                                                          speed_factor_p)

                    active_agents_ids.append(agent.id)

            if agent.HasField('vehicle') and self.param['stop4V']:
                if self.is_vehicle_on_same_lane(ego_vehicle=location, vehicle=agent.vehicle):
                    speed_factor_v = self.stop_vehicle(location, agent, wp_vector, speed_factor_v)

                    active_agents_ids.append(agent.id)

            speed_factor = min(speed_factor_tl, speed_factor_p, speed_factor_v)

        state = {
            'stop_pedestrian': speed_factor_p,
            'stop_vehicle': speed_factor_v,
            'stop_traffic_lights': speed_factor_tl,
            'active_agents_ids': active_agents_ids,
        }

        return speed_factor, state

    """ **********************
        TRAFFIC LIGHT FUNCTIONS
        **********************
    """

    def is_traffic_light_visible(self, location, agent):

        x_agent = agent.traffic_light.transform.location.x
        y_agent = agent.traffic_light.transform.location.y

        _, tl_dist = get_vec_dist(x_agent, y_agent, location.x, location.y)

        return tl_dist > (self.param['tl_min_dist_thres'])

    def is_traffic_light_active(self, location, agent, orientation):
        x_agent = agent.traffic_light.transform.location.x
        y_agent = agent.traffic_light.transform.location.y

        def search_closest_lane_point(x_agent, y_agent, depth):
            step_size = 4
            if depth > 1:
                return None
            try:
                degrees = self._map.get_lane_orientation_degrees([x_agent, y_agent, 38])
            except:
                return None

            if not self._map.is_point_on_lane([x_agent, y_agent, 38]):
                result = search_closest_lane_point(x_agent + step_size, y_agent, depth + 1)
                if result is not None:
                    return result
                result = search_closest_lane_point(x_agent, y_agent + step_size, depth + 1)
                if result is not None:
                    return result
                result = search_closest_lane_point(x_agent + step_size, y_agent + step_size,
                                                   depth + 1)
                if result is not None:
                    return result
                result = search_closest_lane_point(x_agent + step_size, y_agent - step_size,
                                                   depth + 1)
                if result is not None:
                    return result
                result = search_closest_lane_point(x_agent - step_size, y_agent + step_size,
                                                   depth + 1)
                if result is not None:
                    return result
                result = search_closest_lane_point(x_agent - step_size, y_agent, depth + 1)
                if result is not None:
                    return result
                result = search_closest_lane_point(x_agent, y_agent - step_size, depth + 1)
                if result is not None:
                    return result
                result = search_closest_lane_point(x_agent - step_size, y_agent - step_size,
                                                   depth + 1)
                if result is not None:
                    return result
            else:
                if degrees < 6:
                    return [x_agent, y_agent]
                else:
                    return None

        closest_lane_point = search_closest_lane_point(x_agent, y_agent, 0)
        car_direction = math.atan2(orientation.y, orientation.x) + 3.1415
        if car_direction > 6.0:
            car_direction -= 6.0

        return math.fabs(car_direction -
                         self._map.get_lane_orientation_degrees(
                             [closest_lane_point[0], closest_lane_point[1], 38])
                         ) < 1

    # Main function for stopping to traffic lights
    def stop_traffic_light(self, location, agent, wp_vector, wp_angle, speed_factor_tl):

        speed_factor_tl_temp = 1

        if agent.traffic_light.state != 0:  # Not green
            x_agent = agent.traffic_light.transform.location.x
            y_agent = agent.traffic_light.transform.location.y
            tl_vector, tl_dist = get_vec_dist(x_agent, y_agent, location.x, location.y)
            tl_angle = get_angle(tl_vector, wp_vector)

            # CASE 1: Start Slowing down for the traffic light
            if (0 < tl_angle < self.param['tl_angle_thres'] / self.param['coast_factor']
                and tl_dist < self.param['tl_max_dist_thres'] * self.param['coast_factor']) \
                    or (
                    0 < tl_angle < self.param['tl_angle_thres'] and tl_dist < self.param[
                    'tl_max_dist_thres']) and math.fabs(
                                        wp_angle) < 0.2:

                speed_factor_tl_temp = tl_dist / (
                        self.param['coast_factor'] * self.param['tl_max_dist_thres'])

            # CASE 2: Stop Completely for the Traffic Light
            if (0 < tl_angle < self.param['tl_angle_thres'] * self.param[
                'coast_factor'] and tl_dist < self.param['tl_max_dist_thres'] / self.param[
                    'coast_factor']) and math.fabs(
                    wp_angle) < 0.2:
                speed_factor_tl_temp = 0

            if speed_factor_tl_temp < speed_factor_tl:
                speed_factor_tl = speed_factor_tl_temp

        return speed_factor_tl

    def has_burned_traffic_light(self, location, agent, wp_vector, orientation):
        # Not used function, but useful for checking if the traffic light was burned
        def is_on_burning_point(_map, location):

            # We get the current lane orientation
            ori_x, ori_y = _map.get_lane_orientation([location.x, location.y, 38])
            # We test to walk in direction of the lane
            future_location_x = location.x
            future_location_y = location.y
            for i in range(3):
                future_location_x += ori_x
                future_location_y += ori_y
            # Take a point on a intersection in the future
            location_on_intersection_x = future_location_x + 2 * ori_x
            location_on_intersection_y = future_location_y + 2 * ori_y
            if not _map.is_point_on_intersection([future_location_x,
                                                  future_location_y,
                                                  38]) and \
                    _map.is_point_on_intersection([location_on_intersection_x,
                                                   location_on_intersection_y,
                                                   38]):
                return [[future_location_x, future_location_y],
                        [location_on_intersection_x, location_on_intersection_y]
                        ], True

            return [[future_location_x, future_location_y],
                    [location_on_intersection_x, location_on_intersection_y]
                    ], False

        # The vehicle is on not an intersection
        if not self._map.is_point_on_intersection([location.x, location.y, 38]):
            x_agent = agent.traffic_light.transform.location.x
            y_agent = agent.traffic_light.transform.location.y
            tl_vector, tl_dist = get_vec_dist(x_agent, y_agent, location.x, location.y)
            if agent.traffic_light.state != 0:  # Not green

                if self.is_traffic_light_active(location, agent, orientation):

                    positions, burned = is_on_burning_point(self._map, location)
                    if burned and tl_dist < 6.0:
                        return True

        return False
    """ **********************
        PEDESTRIAN FUNCTIONS
        **********************
    """
    def is_pedestrian_hitable(self, pedestrian):

        """
        Determine if a certain pedestrian is in a hitable zone
        Check if pedestrians are on the road (Out of the sidewalk)
        :return:
        """

        x_agent = pedestrian.transform.location.x
        y_agent = pedestrian.transform.location.y

        return self._map.is_point_on_lane([x_agent, y_agent, 38])

    def is_pedestrian_on_hit_zone(self, p_dist, p_angle):
        """
        Draw a semi circle with a big radius but small period from the circunference.
        Pedestrians on this zone will cause the agent to reduce the speed

        """
        return math.fabs(p_angle) < self.param['p_angle_hit_thres'] and \
                    p_dist < self.param['p_dist_hit_thres']

    def is_pedestrian_on_near_hit_zone(self, p_dist, p_angle):

        return math.fabs(p_angle) < self.param['p_angle_eme_thres'] and \
                    p_dist < self.param['p_dist_eme_thres']

    # Main function for stopping for pedestrians
    def stop_pedestrian(self, location, agent, wp_vector, speed_factor_p):

        speed_factor_p_temp = 1
        x_agent = agent.pedestrian.transform.location.x
        y_agent = agent.pedestrian.transform.location.y
        p_vector, p_dist = get_vec_dist(x_agent, y_agent, location.x, location.y)
        p_angle = get_angle(p_vector, wp_vector)
        # CASE 1: Pedestrian is close enough, slow down
        if self.is_pedestrian_on_hit_zone(p_dist, p_angle):
            speed_factor_p_temp = p_dist / (
                    self.param['coast_factor'] * self.param['p_dist_hit_thres'])
        # CASE 2: Pedestrian is very close to the ego-agent
        if self.is_pedestrian_on_near_hit_zone(p_dist, p_angle):
            speed_factor_p_temp = 0

        if speed_factor_p_temp < speed_factor_p:
            speed_factor_p = speed_factor_p_temp

        return speed_factor_p

    """ **********************
        VEHICLE FUNCTIONS
        **********************
    """
    def is_vehicle_on_same_lane(self, ego_vehicle, vehicle):
        """
        Check if the vehicle is on the same lane as the ego_vehicle
        Args:
            ego_vehicle: transform
            vehicle: the other vehicle transformation

        Return:
            Boolean If the vehicle is on the same
        """

        x_agent = vehicle.transform.location.x
        y_agent = vehicle.transform.location.y

        if self._map.is_point_on_intersection([x_agent, y_agent, 38]):
            return True

        return math.fabs(self._map.get_lane_orientation_degrees([ego_vehicle.x, ego_vehicle.y, 38])-
                         self._map.get_lane_orientation_degrees([x_agent, y_agent, 38])) < 1

    def stop_vehicle(self, location, agent, wp_vector, speed_factor_v):

        speed_factor_v_temp = 1
        x_agent = agent.vehicle.transform.location.x
        y_agent = agent.vehicle.transform.location.y
        v_vector, v_dist = get_vec_dist(x_agent, y_agent, location.x, location.y)
        v_angle = get_angle(v_vector, wp_vector)

        # CASE 1: Slowing down for a vehicle (Vehicle Following).
        if (-0.5 * self.param['v_angle_thres'] / self.param['coast_factor'] < v_angle <
                self.param['v_angle_thres'] / self.param['coast_factor'] and v_dist < self.param[
                    'v_dist_thres'] * self.param['coast_factor']) or (
                -0.5 * self.param['v_angle_thres'] / self.param['coast_factor'] < v_angle <
                self.param['v_angle_thres'] and v_dist < self.param['v_dist_thres']):
            speed_factor_v_temp = v_dist / (self.param['coast_factor'] * self.param['v_dist_thres'])

        # CASE 2: Stopping completely for the lead vehicle.
        if (-0.5 * self.param['v_angle_thres'] * self.param['coast_factor'] < v_angle <
                self.param['v_angle_thres'] * self.param['coast_factor'] and v_dist < self.param[
                                                    'v_dist_thres'] / self.param['coast_factor']):
            speed_factor_v_temp = 0

        if speed_factor_v_temp < speed_factor_v:
            speed_factor_v = speed_factor_v_temp

        return speed_factor_v

