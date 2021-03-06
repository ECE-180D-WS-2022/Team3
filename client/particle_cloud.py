from random import randrange

import pygame

from constants import BLUE, GREY, YELLOW


def change_colors(red_delta, green_delta, blue_delta, current_colors):
    def change_color(delta, current_color):
        current_color += delta
        current_color = max(current_color, 0)
        current_color = min(current_color, 255)
        return current_color

    red_out = change_color(red_delta, current_colors[0])
    green_out = change_color(green_delta, current_colors[1])
    blue_out = change_color(blue_delta, current_colors[2])
    return red_out, green_out, blue_out


class Particle:
    def __init__(self, x, y, particle_type):
        self.x = x
        self.y = y
        self.gravity = 0
        self.gravity_delta = 2

        max_velocity = 10
        max_radius = 50

        self.has_gravity = True
        self.radius_delta = -1

        # colors
        self.color = [*BLUE, 255]
        self.red_delta = 10
        self.green_delta = 10
        self.blue_delta = 10
        self.alpha_delta = 5

        if particle_type == 'smoke':
            max_velocity = 5
            max_radius = 50

            self.has_gravity = False
            self.radius_delta = 1

            # colors
            self.color = [*GREY, 150]
            self.red_delta = 10
            self.green_delta = 10
            self.blue_delta = 10
            self.alpha_delta = 5
        elif particle_type == 'fire':
            max_velocity = 10
            max_radius = 50
            self.has_gravity = False
            self.radius_delta = -1

            # colors
            self.color = [*YELLOW, 255]
            self.red_delta = 0
            self.green_delta = -20
            self.blue_delta = 0
            self.alpha_delta = 5
        elif particle_type == 'coin':
            max_velocity = 5
            max_radius = 50

            self.has_gravity = True
            self.gravity_delta = -0.5
            self.radius_delta = -1

            # colors
            self.color = [*YELLOW, 255]
            self.red_delta = 0
            self.green_delta = 0
            self.blue_delta = 0
            self.alpha_delta = 0

        self.x_velocity = randrange(-max_velocity, max_velocity, 1)
        self.y_velocity = randrange(-max_velocity, max_velocity, 1)
        self.radius = randrange(1, max_radius, 1)
        self.valid = True

    def animate(self, surface: pygame.Surface):
        # show particle
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)

        # direction change
        self.x += self.x_velocity
        self.y += self.y_velocity

        # include gravity
        if self.has_gravity:
            self.y -= self.gravity
            self.gravity -= self.gravity_delta

        # color change
        self.color[0:3] = change_colors(
            self.red_delta, self.green_delta, self.blue_delta, self.color[0:3])

        # opacity change
        self.color[3] -= self.alpha_delta

        # size change
        self.radius += self.radius_delta

        # delete particles
        if self.radius < 0 or self.color[3] < 0:
            self.valid = False


class ParticleCloud:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.particles = []
        self.is_smoking = False  # smoke toggle
        self._smoking_count = 0
        self.is_on_fire = False  # fire toggle
        self._on_fire_count = 0
        self.is_coin_bursting = False
        self._coin_burst_count = 0

    def reset(self):
        self.particles = []
        self.is_smoking = False  # smoke toggle
        self._smoking_count = 0
        self.is_on_fire = False  # fire toggle
        self._on_fire_count = 0
        self.is_coin_bursting = False
        self._coin_burst_count = 0

    def smoke_cloud(self, frames):
        self._smoking_count = frames

    def fire_burst(self, frames):
        self._on_fire_count = frames

    def coin_burst(self, frames):
        self._coin_burst_count = frames

    def show(self, surface):
        if self.is_smoking or self._smoking_count > 0:
            new_particle = Particle(self.x, self.y, 'smoke')
            self.particles.append(new_particle)
            self._smoking_count -= 1 if self._smoking_count > 0 else 0

        if self.is_on_fire or self._on_fire_count > 0:
            new_particle = Particle(self.x, self.y, 'fire')
            self.particles.append(new_particle)
            self._on_fire_count -= 1 if self._on_fire_count > 0 else 0

        if self.is_coin_bursting or self._coin_burst_count > 0:
            new_particle = Particle(self.x, self.y, 'coin')
            self.particles.append(new_particle)
            self._coin_burst_count -= 1 if self._coin_burst_count > 0 else 0

        for particle in self.particles:
            particle.animate(surface)
        self.particles = [
            particle for particle in self.particles if particle.valid]
