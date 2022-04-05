from random import choice

from Cloud import *
from Controller import *
from OpponentRanger import *
from Player import *
from ScreenManager import *
from ServerIface import *


class GameMultiplayer:
    def __init__(self, screen_width=1280, screen_height=720,
                 window_title='Sky Danger Ranger - '):

        # Ask user if they want to join game or create new one
        # 0 is created new game, 1 is join new game
        self.voice = VoiceIface()
        self.enemy_types = None
        self.enemy_info = None
        self.use_voice = input(
            'do you want to use voice? (yes or no) ').lower() == 'yes'
        asking = True
        while asking:
            print(
                "Would you like to join an existing game(join) or create a new game(create)?: ")
            if self.use_voice:
                self.is_host = self.voice.find_word('create')
            else:
                self.is_host = ''.join(input()).lower() == 'create'
            if self.is_host:
                room_id_question = "Pick a room ID for everyone to join!: "
            else:
                room_id_question = "What is the room ID that you'd like to join?: "
            print(room_id_question)
            if self.use_voice:
                room_id = self.voice.listen()
            else:
                room_id = input()
            print("What username would you like to use?")
            if self.use_voice:
                username = self.voice.listen()
            else:
                username = input()
            self.username = "_".join(username.split())
            self.room_id = "".join(room_id.split())
            print(
                "is host:",
                self.is_host,
                "room id",
                self.room_id,
                "username",
                self.username)
            if self.room_id and self.username:
                asking = False
            else:
                print('try that again')

        # pygame initialization
        pygame.init()
        show_mouse(True)
        pygame.display.set_caption(
            window_title + self.room_id + ':' + self.username)
        pygame.display.set_icon(
            pygame.image.load(ranger_path)
        )

        # Server setup
        self.server = ServerIface(self.username)
        self.server.fetch_enemies()  # Make socket call to fetch and set enemy types
        self.server.connect(self.room_id, self.is_host)  # connect to room
        self.enemy_id_count = 0

        self.clock = pygame.time.Clock()
        self.clouds = []
        self.enemies = []
        self.frame_rate = 60
        self.max_spawn_counter = 100
        self.num_clouds = 8
        self.num_z_levels = 1
        self.opponent_rangers = []
        self.screen_height = screen_height
        self.screen_width = screen_width

        self.controller = Controller(self.num_z_levels)
        self.screen_manager = ScreenManager(
            sky_path, self.screen_width, self.screen_height)
        self.spawn_counter = self.max_spawn_counter
        self.db = DatabaseIface()
        self.player = Player(
            screen_width,
            screen_height,
            self.db,
            self.num_z_levels)

    def add_enemy(self, enemy: MultiplayerEnemy):
        self.enemies.append(enemy)

    def add_opponent_rangers(self, opponent: OpponentRanger):
        self.opponent_rangers.append(opponent)

    def add_cloud(self, cloud: Cloud):
        self.clouds.append(cloud)

    def run(self):
        # Did here so self.server.serverEnemies is not null,
        # tried it in init & didn't work
        self.enemy_info = self.server.server_enemies
        self.enemy_types = list(self.enemy_info.keys())

        # create clouds
        for _ in range(self.num_clouds):
            screen_x, screen_y = self.screen_manager.screen_dimensions
            self.add_cloud(
                Cloud(
                    randrange(0, screen_x, 1),
                    randrange(0, screen_y, 1),
                    0,
                    self.num_z_levels,
                    cloud_path
                )
            )

        # game loop
        running = True
        while running:
            # event handler
            for event in pygame.event.get():
                # check for window close
                if event.type == pygame.QUIT:
                    running = False

            self.clock.tick(self.frame_rate)
            self.screen_manager.render_background()
            self.spawn_counter -= 1

            # render each cloud
            for cloud in self.clouds:
                cloud.show(self.screen_manager.surface)
                cloud.loop_around(self.screen_width, self.screen_height)

            # spawn an enemy every self.max_spawn_counter frames
            if self.spawn_counter <= 0:
                # If you are host, you can spawn new enemies
                if self.server.is_host:
                    self.spawn_counter = self.max_spawn_counter
                    current_enemy_type = choice(self.enemy_types)
                    new_enemy = MultiplayerEnemy(
                        randrange(
                            0,
                            self.screen_width,
                            1),
                        100,
                        0,
                        1,
                        current_enemy_type,
                        self.enemy_info,
                        self.enemy_id_count
                    )
                    self.enemies.append(new_enemy)
                    self.server.append_new_enemy_to_server(new_enemy)
                    self.enemy_id_count += 1

            # ranger movement
            x, y = self.controller.get_xy(
                self.screen_width, self.screen_width,
                self.player.ranger.x, self.player.ranger.y,
                self.player.speed, self.player.max_speed
            )
            if self.controller.is_moving():
                # gradually increase speed when holding down key
                self.player.speed *= self.player.acceleration
            else:
                # reset speed
                self.player.speed = self.player.min_speed
            # update ranger coordinates
            self.player.ranger.update_coordinates(x, y)
            # update server coordinates
            self.server.send_location_and_meta(
                x, y, self.player.ranger.z, self.controller.is_firing())

            # show laser
            self.player.ranger.fire(
                self.controller.is_firing(),
                self.screen_manager.surface
            )

            ################################################
            # Handle enemies
            ################################################
            self.server.fetch_all_entities()
            # display all enemies
            for enemy in self.enemies:
                enemy.countdown_time_alive()
                enemy.step(self.screen_manager.screen_dimensions)
                # Update server on where enemy stepped
                enemy_coordinates = enemy.get_coordinates()
                self.server.update_enemy_coordinates(
                    enemy.id, enemy_coordinates[0], enemy_coordinates[1])
                if enemy.should_display:
                    # detect laser hits
                    if self.player.ranger.laser_is_deadly and self.player.ranger.x in enemy.get_x_hitbox():
                        damage = 1
                        enemy.got_hit(damage)
                        self.player.current_score += enemy.handle_death()
                else:
                    # remove dead and timed out enemies
                    self.enemies.remove(enemy)
                    if self.server.is_host:
                        self.server.remove_enemy_from_server(enemy.id)

            for enemy in self.server.host_enemies:
                enemy.show(self.screen_manager.surface)

                # Update server on where enemy stepped
                if enemy.should_display:
                    # detect laser hits
                    if self.player.ranger.laser_is_deadly and self.player.ranger.x in enemy.get_x_hitbox():
                        damage = 1
                        enemy.got_hit(damage)
                        self.player.current_score += enemy.handle_death()
                else:
                    # Not only host, if you hit it, you can remove it
                    self.server.remove_enemy_from_server(enemy.id)
            ################################################

            # show ranger
            self.player.ranger.show(self.screen_manager.surface)

            ################################################
            # Handle opponent rangers
            ################################################
            self.server.fetch_ranger_opponents()
            self.opponent_rangers = self.server.opponent_rangers

            # Update Ranger Opponents list
            opponent_dict = {}
            for opponent_ranger in self.opponent_rangers:
                if opponent_ranger not in opponent_dict:
                    opponent = Player(
                        self.screen_width,
                        self.screen_height,
                        self.db,
                        self.num_z_levels)
                    opponent_dict[opponent_ranger] = opponent
            # Show and update coordinates of Ranger Opponents
            for opp in opponent_dict:
                try:
                    coordinates_and_meta = self.server.opponent_ranger_coordinates[opp]
                    opponent_dict[opp].ranger.update_coordinates(
                        coordinates_and_meta[0],
                        coordinates_and_meta[1]
                    )
                    opponent_dict[opp].ranger.fire(
                        coordinates_and_meta[3],
                        self.screen_manager.surface
                    )
                    opponent_dict[opp].ranger.show(self.screen_manager.surface)

                except BaseException:
                    # for when opponent_ranger_coordinates is not yet updated,
                    # we can try again on next rendering
                    continue

            # uncomment this to print out all opponent rangers' socketIDs
            # print('list of opponent rangers',self.server.opponent_rangers)
            ################################################

            # show current score
            self.screen_manager.render_score(self.player.current_score)

            # update display
            pygame.display.update()

        print('quitting')
        self.server.disconnect()
        self.controller.disconnect()
        pygame.quit()
        quit()
