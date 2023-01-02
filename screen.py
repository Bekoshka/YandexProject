import sys

import pygame

from common import all_sprites, monster_group, landscape_sprites, obstacle_group, player_group
from landscape import Landscape
from player import Player, Monster
from settings import WIDTH, HEIGHT, FPS, STEP
from tiles import Weapon, SLOT_LEFT_HAND, HealPotion, SLOT_RIGHT_HAND, Armor, SLOT_ARMOR
from utils import load_image


class StartScreen:
    def __init__(self, screen):
        self.screen = screen
        self.intro_text = ["ЗАСТАВКА", "",
                      "Правила игры",
                      "Если в правилах несколько строк,",
                      "приходится выводить их построчно"]

    def run(self):
        fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
        self.screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 30)
        text_coord = 50
        for line in self.intro_text:
            string_rendered = font.render(line, True, pygame.Color('white'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            self.screen.blit(string_rendered, intro_rect)

        pygame.display.flip()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                elif event.type == pygame.KEYDOWN or \
                        event.type == pygame.MOUSEBUTTONDOWN:
                    return  # начинаем игру

    def terminate(self):
        pygame.quit()
        sys.exit()


class Camera:
    def __init__(self, focus, other):
        self.focus = focus
        self.other = other
        self.dx = 0
        self.dy = 0
        self.follow()

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)

    def follow(self):
        self.update(self.focus)
        for sprite in self.other:
            self.apply(sprite)


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.landscape = Landscape()
        self.landscape.generate_level()
        self.monsters = [Monster(3, 4)]
        self.player = Player(3, 5)
        sword = Weapon("sword", "sword description", None, (15, 20), 50, SLOT_LEFT_HAND)
        pot = HealPotion("ho", "hp desc", None, 10, SLOT_LEFT_HAND | SLOT_RIGHT_HAND)
        armor = Armor("armor", "armor description", None, 15, SLOT_ARMOR)
        self.player.ammunition.assign(sword, 1)
        self.player.ammunition.assign(pot, 3)
        self.monsters[0].ammunition.assign(armor, 2)

        self.camera = Camera(self.player, all_sprites)
        self.clock = pygame.time.Clock()
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            self.handle_events()
            self.render()
            self.clock.tick(FPS)

    def render(self):
        self.screen.fill(pygame.Color(0, 0, 0))
        landscape_sprites.draw(self.screen)
        obstacle_group.draw(self.screen)
        monster_group.draw(self.screen)
        player_group.draw(self.screen)
        all_sprites.update(self.screen)
        pygame.display.flip()

    def handle_events(self):
        dx, dy = 0, 0
        enemy = None
        button = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_RIGHT]:
            dx += 1
        if keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_DOWN]:
            dy += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in [1, 3]:
                    for monster in monster_group:
                        if monster.rect.collidepoint(event.pos):
                            enemy = monster
                            button = event.button

        if enemy:
            self.player.attack(enemy, button)
        else:
            self.player.step(dx, dy)
            self.camera.follow()



# TODO attack in move animation and not move animation
# TODO FIX health bar animation

