import random

import pygame.surface

from paths import opponent_path
from ranger import Ranger


class OpponentRanger(Ranger):
    def __init__(
            self,
            x,
            y,
            z,
            num_z_levels,
            ranger_id,
            image_path=opponent_path):
        self.ranger_id: int = ranger_id

        super().__init__(x, y, z, num_z_levels, image_path)

    def fire(self, *args, **kwargs):
        # set random seed to be the ranger id so each ranger has their own
        # color laser
        random.seed(self.ranger_id)
        super().fire(
            *args,
            **kwargs,
            color=(
                random.randint(
                    0,
                    255),
                random.randint(
                    0,
                    255),
                random.randint(
                    0,
                    255)))
        # reset random seed
        random.seed(None)

    def show_diff_level(self, surface: pygame.surface.Surface,
                        particle_surface: pygame.surface.Surface, cur_z: int):
        if self.z == cur_z:
            super().show(surface, particle_surface)
            return
        is_above = self.z > cur_z
        if is_above:
            self.shape.set_alpha(255 // 2)
            text = 'above'
        else:
            self.shape.set_alpha(255 // 4)
            text = 'below'
        super().show(surface, particle_surface)
        self.shape.set_alpha(255)
        # indicate above or below
        font = pygame.font.SysFont('Comic Sans', 20)
        rendered_font = font.render(f'{text}', True, (255, 255, 255))
        surface.blit(
            rendered_font,
            (self.rect.centerx -
             rendered_font.get_width() //
             2,
             self.rect.bottom))
