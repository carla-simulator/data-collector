
class CollisionChecker(object):

    def __init__(self):

        self.first_iter = True
        # The parameters used for the case we want to detect collisions
        self._thresh_other = 400
        self._thresh_vehicle = 400
        self._thresh_pedestrian = 300
        self._previous_pedestrian_collision = 0
        self._previous_vehicle_collision = 0
        self._previous_other_collision = 0

        self._collision_time = -1
        self._count_collisions = 0




    def test_collision(self, player_measurements):
        """
            test if there is any instant collision.

        """
        collided = False

        if (player_measurements.collision_vehicles - self._previous_vehicle_collision) \
                > self._thresh_vehicle:
            collided = True
        if (player_measurements.collision_pedestrians - self._previous_pedestrian_collision) \
                > self._thresh_pedestrian:
            collided = True
        if (player_measurements.collision_other - self._previous_other_collision) \
                > self._thresh_other:
            collided = True

        self._previous_pedestrian_collision = player_measurements.collision_pedestrians
        self._previous_vehicle_collision = player_measurements.collision_vehicles
        self._previous_other_collision = player_measurements.collision_other

        return collided




