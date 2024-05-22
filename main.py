import os
import asyncio
import cv2
import numpy # cv2
import pygame
import random

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 860
FPS = 30

current_directory = os.path.dirname(__file__)

fonts_directory = os.path.join(current_directory, 'fonts')
images_directory = os.path.join(current_directory, 'images')
cats_directory = os.path.join(images_directory, 'cats')
sounds_directory = os.path.join(current_directory, 'sounds')
video_directory = os.path.join(current_directory, 'video')


class Tile(pygame.sprite.Sprite):
    def __init__(self, filename, x, y):
        super().__init__()
        self.name = filename.split('.')[0]
        self.original_image = pygame.image.load(os.path.join(cats_directory, filename))
        self.back_image = pygame.Surface((128, 128))
        self.back_image.fill(WHITE)
        self.back_image.set_alpha(128)
        self.image = self.back_image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.shown = False

    def update(self):
        self.image = self.original_image if self.shown else self.back_image

    def show(self):
        self.shown = True

    def hide(self):
        self.shown = False


class Game():
    def __init__(self):
        self.level = 1
        self.level_complete = False

        self.all_cats = [f for f in os.listdir(cats_directory) if os.path.isfile(os.path.join(cats_directory, f))]
        self.img_width, self.img_height = (128, 128)
        self.padding = 20
        self.margin_top = 150
        self.cols = 4
        self.rows = 2
        self.width = 1280

        self.tiles_group = pygame.sprite.Group()

        self.flipped = []
        self.frame_count = 0
        self.block_game = False

        self.generate_level(self.level)

        self.is_video_playing = True
        self.play = pygame.image.load(os.path.join(images_directory, 'play.png')).convert_alpha()
        self.stop = pygame.image.load(os.path.join(images_directory, 'stop.png')).convert_alpha()
        self.video_toggle = self.play
        self.video_toggle_rect = self.video_toggle.get_rect(topright=(WINDOW_WIDTH - 50, 10))

        self.get_video()

        self.is_music_playing = True
        self.sound_on = pygame.image.load(os.path.join(images_directory, 'speaker.png')).convert_alpha()
        self.sound_off = pygame.image.load(os.path.join(images_directory, 'mute.png')).convert_alpha()
        self.music_toggle = self.sound_on
        self.music_toggle_rect = self.music_toggle.get_rect(topright=(WINDOW_WIDTH - 10, 10))

        pygame.mixer.music.load(os.path.join(sounds_directory, 'audio.mp3'))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(loops=-1)

    def update(self, event_list):
        if self.is_video_playing:
            self.success, self.img = self.cap.read()

        self.user_input(event_list)
        self.draw()
        self.check_level_complete(event_list)

    def check_level_complete(self, event_list):
        if not self.block_game:
            for event in event_list:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for tile in self.tiles_group:
                        if tile.rect.collidepoint(event.pos):
                            self.flipped.append(tile.name)
                            tile.show()
                            if len(self.flipped) == 2:
                                if self.flipped[0] != self.flipped[1]:
                                    self.block_game = True
                                else:
                                    self.flipped = []
                                    for tile in self.tiles_group:
                                        if tile.shown:
                                            self.level_complete = True
                                        else:
                                            self.level_complete = False
                                            break
        else:
            self.frame_count += 1
            if self.frame_count == FPS:
                self.frame_count = 0
                self.block_game = False
                for tile in self.tiles_group:
                    if tile.name in self.flipped:
                        tile.hide()
                self.flipped = []

    def generate_level(self, level):
        self.cats = self.select_random_cats(self.level)
        self.level_complete = False
        self.rows = self.level + 1
        self.cols = 4
        self.generate_tileset(self.cats)

    def generate_tileset(self, cats):
        TILES_WIDTH = (self.img_width * self.cols + self.padding * 3)
        LEFT_MARGIN = (self.width - TILES_WIDTH) / 2
        self.tiles_group.empty()
        for i in range(len(cats)):
            x = LEFT_MARGIN + ((self.img_width + self.padding) * (i % self.cols))
            y = self.margin_top + ((i // self.cols) * (self.img_height + self.padding))
            tile = Tile(cats[i], x, y)
            self.tiles_group.add(tile)

    def select_random_cats(self, level):
        cats = random.sample(self.all_cats, (self.level + self.level + 2))
        cats_copy = cats.copy()
        cats.extend(cats_copy)
        random.shuffle(cats)
        return cats

    def user_input(self, event_list):
        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.music_toggle_rect.collidepoint(pygame.mouse.get_pos()):
                    if self.is_music_playing:
                        self.is_music_playing = False
                        self.music_toggle = self.sound_off
                        pygame.mixer.music.pause()
                    else:
                        self.is_music_playing = True
                        self.music_toggle = self.sound_on
                        pygame.mixer.music.unpause()
                if self.video_toggle_rect.collidepoint(pygame.mouse.get_pos()):
                    if self.is_video_playing:
                        self.is_video_playing = False
                        self.video_toggle = self.stop
                    else:
                        self.is_video_playing = True
                        self.video_toggle = self.play
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.level_complete:
                    self.level += 1
                    if self.level >= 6:
                        self.level = 1
                    self.generate_level(self.level)

    def draw(self):
        screen.fill(BLACK)
        title_font = pygame.font.Font(os.path.join(fonts_directory, 'Sugar Cream.otf'), 44)
        content_font = pygame.font.Font(os.path.join(fonts_directory, 'Sugar Cream.otf'), 24)

        title_text = title_font.render('MiXel Memory Game', True, WHITE)
        title_rect = title_text.get_rect(midtop=(WINDOW_WIDTH / 2, 10))
        level_text = content_font.render('Level ' + str(self.level), True, WHITE)
        level_rect = level_text.get_rect(midtop=(WINDOW_WIDTH / 2, 80))
        info_text = content_font.render('Find 2 of each', True, WHITE)
        info_rect = info_text.get_rect(midtop=(WINDOW_WIDTH / 2, 120))

        screen.blit(title_text, title_rect)
        screen.blit(level_text, level_rect)
        screen.blit(info_text, info_rect)

        if self.is_video_playing:
            if self.success:
                screen.blit(pygame.image.frombuffer(self.img.tobytes(), self.shape, 'BGR'), (100, 150))
            else:
                self.get_video()
        else:
            screen.blit(pygame.image.frombuffer(self.img.tobytes(), self.shape, 'BGR'), (100, 150))

        if self.level_complete:
            if self.level != 5:
                next_text = content_font.render('Level complete. Press space for next level.', True, WHITE)
            else:
                next_text = content_font.render('Congrats. You won. Press space to play again.', True, WHITE)
            next_rect = next_text.get_rect(midbottom=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 40))
            screen.blit(next_text, next_rect)

        pygame.draw.rect(screen, WHITE, (WINDOW_WIDTH - 90, 0, 100, 50))
        screen.blit(self.music_toggle, self.music_toggle_rect)
        screen.blit(self.video_toggle, self.video_toggle_rect)

        self.tiles_group.draw(screen)
        self.tiles_group.update()

    def get_video(self):
        video_path = os.path.join(video_directory, 'video.mp4')
        self.cap = cv2.VideoCapture(video_path)
        self.success, self.img = self.cap.read()
        self.shape = self.img.shape[1::-1]


pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("MiXel Memory Game")
clock = pygame.time.Clock()

game = Game()

async def main():
    running = True
    while running:
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                running = False
        game.update(event_list)
        pygame.display.update()
        clock.tick(FPS)
        await asyncio.sleep(0)

asyncio.run(main())
pygame.quit()