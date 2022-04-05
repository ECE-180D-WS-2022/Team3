import socketio

from MultiplayerEnemy import *


# TODO -- create this class or decide on whether or not to delete it


class ServerIface:
    def __init__(self, username):
        self.socket = socketio.Client()
        # Localhost
        self.socket.connect('http://localhost:8000')
        # Production
        # self.socket.connect('https://skydangerranger.herokuapp.com/')
        self.server_enemies = None
        self.is_host = False
        self.room_id = ''
        self.socket_id = ''
        self.opponent_rangers = []
        self.opponent_ranger_coordinates = {}
        self.username = username

        # Will be all enemies spawned on host
        # everyone else uses host's enemies
        self.host_enemies = []

        self.id_mapping = {
            'jc': {
                'death_sound_path': jc_death_sound_path,
                'image_path': jc_path
            },
            'cow': {
                'death_sound_path': friendly_fire_sound_path,
                'image_path': cow_path
            },
            'ricky': {
                'death_sound_path': ricky_death_sound_path,
                'image_path': ricky_path
            },
            'david': {
                'death_sound_path': wrong_answer_sound_path,
                'image_path': david_path
            },
            'anton': {
                'death_sound_path': anton_death_sound_path,
                'image_path': anton_path
            },
            'armando': {
                'death_sound_path': friendly_fire_sound_path,
                'image_path': armando_path
            },
            'david2': {
                'death_sound_path': david2_death_sound_path,
                'image_path': david2_path
            },
        }

        @self.socket.on("welcome_client")
        def on_welcome(data):
            print("Server: ", data['message'])
            print("Socket ID: ", data['socket_id'])
            self.socket_id = data['socket_id']

        @self.socket.on("enemy_info_to_client")
        def set_enemies_from_server(data):
            for enemy in data:
                data[enemy]["death_sound_path"] = self.id_mapping[enemy]["death_sound_path"]
                data[enemy]["image_path"] = self.id_mapping[enemy]["image_path"]
            self.server_enemies = data

        @self.socket.on("server_sending_opponent_rangers_in_game")
        def set_opponent_rangers(data):
            opponent_rangers = []
            for ranger in data["list"]:
                if ranger != self.socket_id:
                    opponent_rangers.append(ranger)
            self.opponent_rangers = opponent_rangers

        @self.socket.on("update_opponent_ranger_coordinates")
        def update_opponent_ranger_coordinates(data):
            # set coordinates of opponent rangers
            self.opponent_ranger_coordinates[data["socket_id"]] = (
                data['x'],
                data['y'],
                data['z'],
                data['is_firing']
            )

        @self.socket.on("all_entities_to_client")
        def receiving_all_entities(data):
            # HANDLING ENEMIES
            # two steps
            # 1: remove old enemies
            # 2: add new enemies
            # 3 update coordinates of existing entities

            # remove old enemies
            # find which enemies on local version are no longer on server
            # version & remove them
            new_enemies = []
            # do this in reverse, so we don't skip any on deleting
            i = len(self.host_enemies) - 1
            while i >= 0:
                curr_enemy = self.host_enemies[i]
                # print(curr_enemy.id, data["enemies"].keys(), 'bees')
                if curr_enemy.id not in data["enemies"]:
                    self.host_enemies.pop(i)
                i -= 1

            # add new enemies
            # find new opponents
            # find enemy IDs in data["enemies"] that is not in host_enemies,
            # add new enemy object
            host_enemy_ids = list(data["enemies"].keys())
            for enemy in self.host_enemies:
                try:
                    host_enemy_ids.remove(enemy.id)
                except BaseException:
                    continue

            # all existing ids have been removed
            for new_enemy_id in host_enemy_ids:
                enemy_data = data["enemies"][new_enemy_id]

                # new enemy
                new_enemy = MultiplayerEnemy(
                    enemy_data['x'],
                    enemy_data['y'],
                    enemy_data['z'],
                    enemy_data['num_z_levels'],
                    enemy_data['enemy_type'],
                    self.server_enemies,
                    new_enemy_id
                )
                self.host_enemies.append(new_enemy)

            for enemy in self.host_enemies:
                enemy.update_coordinates(
                    data["enemies"][enemy.id]['x'], data["enemies"][enemy.id]['y'])

    def connect(self, room_id, is_host):
        event_name = "join_new_room" if is_host else "join_existing_room"
        self.is_host = is_host
        self.room_id = room_id
        self.socket.emit(event_name, {
            'room_id': room_id
        })

    def fetch_enemies(self):
        self.socket.emit('fetch_enemies')

    def send_location_and_meta(self, x, y, z, is_firing):
        self.socket.emit("update_my_coordinates_and_meta", {
            'x': x,
            'y': y,
            'z': z,
            'is_firing': is_firing
        })

    def fetch_ranger_opponents(self):
        self.socket.emit("fetch_opponent_rangers")

    def fetch_all_entities(self):
        self.socket.emit('fetch_all_entities')

    def append_new_enemy_to_server(self, enemy):
        if self.is_host:
            coordinates = enemy.get_coordinates()
            stripped_enemy = {
                'x': coordinates[0],
                'y': coordinates[1],
                'z': coordinates[2],
                'id': enemy.id,
                'enemy_type': enemy.enemy_type,
                'health': enemy.health,
                'num_z_levels': enemy.num_z_levels
            }
            self.socket.emit('host_appending_new_enemy', stripped_enemy)

    def update_enemy_coordinates(self, id, x, y):
        if self.is_host:
            self.socket.emit("host_updating_enemy_coordinates", {
                'id': id,
                'x': x,
                'y': y
            })

    def remove_enemy_from_server(self, id):
        self.socket.emit('remove_enemy', {"id": id})

    def disconnect(self):
        self.socket.disconnect()
