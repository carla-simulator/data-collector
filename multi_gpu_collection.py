import argparse
import time
import logging
import subprocess
import multiprocessing

from carla.client import make_carla_client
from carla.tcp import TCPConnectionError

from collect import collect


class Arguments():
    # Some replacement to the arguments input to simplify the interface.
    def __init__(self, port, number_of_episodes, episode_number, path_name,
                 data_configuration_name):
        self.port = port
        self.host = 'localhost'
        self.number_of_episodes = number_of_episodes
        self.episode_number = episode_number
        self.not_record = False
        self.debug = False
        self.verbose = False
        self.controlling_agent = 'CommandFollower'
        self.data_path = path_name
        self.data_configuration_name = data_configuration_name


def collect_loop(args):
    while True:
        try:
            with make_carla_client(args.host, args.port) as client:
                collect(client, args)
                break

        except TCPConnectionError as error:
            logging.error(error)
            time.sleep(1)

def execute_collector(args):
    p = multiprocessing.Process(target=collect_loop,
                                args=(args,))
    p.start()

# open a carla docker with the container_name
def open_carla(port, town_name, gpu, container_name):
    sp = subprocess.Popen(
        ['docker', 'run', '--rm', '-d', '-p',
         str(port) + '-' + str(port + 2) + ':' + str(port) + '-' + str(port + 2),
         '--runtime=nvidia', '-e', 'NVIDIA_VISIBLE_DEVICES=' + str(gpu), container_name,
         '/bin/bash', 'CarlaUE4.sh', '/Game/Maps/' + town_name, '-windowed',
         '-benchmark', '-fps=10', '-world-port=' + str(port)], shell=False,
        stdout=subprocess.PIPE)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        description='Release Data Collectors')
    argparser.add_argument(
        '-n', '--number_collectors',
        default=1,
        type=int,
        help=' the number of collectors used')
    argparser.add_argument(
        '-e', '--number_episodes',
        default=200,
        type=int,
        help=' the number of episodes per collector used')
    argparser.add_argument(
        '-g', '--carlas_per_gpu',
        default=3,
        type=int,
        help=' number of gpus per carla')
    argparser.add_argument(
        '-s', '--start_episode',
        default=0,
        type=int,
        help=' the first episode')
    argparser.add_argument(
        '-d', '--data-configuration-name',
        dest='data_configuration_name',
        default='coil_training_dataset',
        help=' the first episode')
    argparser.add_argument(
        '-pt', '--data-path',
        dest='data_path',
        default='/mnt/parallel/CARLA/',
        help='The path used to save the data')
    argparser.add_argument(
        '-ct', '--container-name',
        dest='container_name',
        default='carlagear',
        help='The name of the docker container used to collect data')
    argparser.add_argument(
        '-t', '--town_name',
        default=1,
        type=int,
        help=' the town name')

    args = argparser.parse_args()

    town_name = 'Town0' + str(args.town_name)

    for i in range(args.number_collectors):
        port = 2000 + i * 3
        gpu = str(int(i / args.carlas_per_gpu))
        collector_args = Arguments(port, args.number_episodes,
                                   args.start_episode + (args.number_episodes) * (i),
                                   args.data_path,
                                   args.data_configuration_name)
        execute_collector(collector_args)
        open_carla(port, town_name, gpu, args.container_name)
