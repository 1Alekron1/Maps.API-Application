import pygame
import requests
import os

pygame.init()
MAP_SIZE = (650, 450)
SCREEN_SIZE = (1300, 450)
screen = pygame.display.set_mode(SCREEN_SIZE)


class ImageMap:
    def __init__(self):
        self.blit_cords = (int(SCREEN_SIZE[0] * 0.25), 0)
        self.data = ''
        self.link = "https://static-maps.yandex.ru/1.x/?"
        self.params = {
            "ll": "37.62684248809827,55.75551062887589",
            "l": "map",
            "z": "12",
            "size": ",".join(map(str, MAP_SIZE)),
            "pt": ''
        }
        self.image = None
        self.move = 204
        self.value_changed()

    def create_image(self, response):
        with open('filename.png', 'wb') as f:
            f.write(response.content)
        self.image = pygame.image.load('filename.png')
        os.remove('filename.png')

    def value_changed(self):
        self.create_image(requests.get(create_request(self)))

    def change_pos(self, value):
        temp_cords = list(map(float, self.params["ll"].split(',')))
        temp_move = self.move / (2 ** (int(self.params['z']) + 1.5))
        if value == pygame.K_w:
            if -90 < temp_cords[1] + temp_move < 90:
                temp_cords[1] += temp_move
        elif value == pygame.K_s:
            if -90 < temp_cords[1] - temp_move < 90:
                temp_cords[1] -= temp_move
        elif value == pygame.K_a:
            temp_move = self.move / (2 ** (int(self.params['z']) + 0.5))
            if -180 < temp_cords[1] - temp_move < 180:
                temp_cords[0] -= temp_move
        elif value == pygame.K_d:
            temp_move = self.move / (2 ** (int(self.params['z']) + 0.5))
            if -180 < temp_cords[1] + temp_move < 180:
                temp_cords[0] += temp_move
        self.params["ll"] = ','.join(map(str, temp_cords))
        self.value_changed()
        pass


def create_request(self):
    link = self.link
    for i in self.params:
        if self.params[i]:
            link += i
            link += '='
            link += self.params[i]
            link += '&'
    return link.rstrip('&')


class Geocoder:
    def __init__(self):
        self.link = "https://geocode-maps.yandex.ru/1.x/?"
        self.params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "format": "json",
            "geocode": ""
        }


class Button:
    def __init__(self, pos, size, size1, typ, text):
        self.image = pygame.Surface((size, size1))
        self.image.fill(pygame.Color("white"))
        self.rect = self.image.get_rect(topleft=pos)
        self.typ = typ
        self.l_var = ["map", "sat", "skl"]
        self.count = 0
        self.color = pygame.Color('white')
        self.text = font.render(text, True, pygame.Color('orange'))

    def collide(self, pos):
        if self.rect.collidepoint(pos):
            if self.typ == 0:
                self.change_l()
            if self.typ == 1:
                self.reset()

    def change_l(self):
        self.count = (self.count + 1) % 3
        image_map.params["l"] = self.l_var[self.count]
        image_map.value_changed()

    @staticmethod
    def reset():
        image_map.params['pt'] = ''
        image_map.value_changed()

    def draw(self, scr):
        pygame.draw.rect(scr, self.color, self.rect, 2, 3)
        scr.blit(self.text, (self.rect.x + 3, self.rect.y + 5))


class InputField:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = pygame.Color(67, 67, 67)
        self.color_active = pygame.Color(157, 157, 157)
        self.font = pygame.font.Font(None, 25)
        self.color = self.color_inactive
        self.text = ''
        self.txt_surface = self.font.render(self.text, True, self.color)
        self.active = False

    def handle_event(self, eve):
        if eve.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(eve.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
        if eve.type == pygame.KEYDOWN:
            if self.active:
                if eve.key == pygame.K_RETURN:
                    self.request_js(self.text)
                    self.text = ''
                elif eve.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += eve.unicode
                self.txt_surface = self.font.render(self.text, True, self.color)

    def update(self):
        width = max(150, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, scr):
        pygame.draw.rect(scr, self.color, self.rect, 2, 3)
        scr.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))

    @staticmethod
    def request_js(text):
        geocode.params["geocode"] = text
        response = requests.get(create_request(geocode))
        if response:
            json_response = response.json()
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0][
                "GeoObject"]
            toponym_coodrinates = ','.join(toponym["Point"]["pos"].split())
            image_map.params['ll'] = toponym_coodrinates
            image_map.params['pt'] = toponym_coodrinates
            image_map.value_changed()


image_map = ImageMap()
running = True
font = pygame.font.Font(None, 20)
button_group = [Button((30, 100), 150, 30, 0, 'схема/спутник/гибрид'),
                Button((1005, 50), 200, 30, 1, 'сброс поискового результата')]
reset_button = font.render('сброс поискового результата', True, pygame.Color('orange'))
input_field = InputField(30, 50, 150, 30)
geocode = Geocoder()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        key = pygame.key.get_pressed()
        input_field.handle_event(event)
        # стрелки вверх, вниз увеличивают и уменьшают масштаб карты соответственно
        if key[pygame.K_DOWN]:
            if image_map.params['z'] != "0":
                image_map.params['z'] = str(int(image_map.params['z']) - 1)
                image_map.value_changed()
        elif key[pygame.K_UP]:
            if image_map.params['z'] != "17":
                image_map.params['z'] = str(int(image_map.params['z']) + 1)
                image_map.value_changed()
        # клашиви w,a,s,d двигают центр карты вверх, влево, вниз, вправо соответственно
        elif key[pygame.K_w]:
            image_map.change_pos(pygame.K_w)
        elif key[pygame.K_s]:
            image_map.change_pos(pygame.K_s)
        elif key[pygame.K_a]:
            image_map.change_pos(pygame.K_a)
        elif key[pygame.K_d]:
            image_map.change_pos(pygame.K_d)
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in button_group:
                button.collide(event.pos)
    screen.blit(image_map.image, image_map.blit_cords)
    for button in button_group:
        button.draw(screen)
    input_field.update()
    input_field.draw(screen)
    pygame.display.update()
    pygame.display.flip()
    screen.fill(pygame.Color('black'))
pygame.quit()
