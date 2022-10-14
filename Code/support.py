import pygame


def import_cut_graphics(path: str, sprite_width: int, sprite_height: int, flip=False) -> list:
    pygame.init()
    image = pygame.image.load(path).convert_alpha()
    if flip:
        image = pygame.transform.flip(image, True, False)
    tile_num_x = image.get_size()[0] // sprite_width
    tile_num_y = image.get_size()[1] // sprite_height
    cut_images = []
    for row in range(tile_num_y):
        for col in range(tile_num_x):
            x = col * sprite_width
            y = row * sprite_height
            cut = pygame.Surface((sprite_width, sprite_height))
            cut.set_colorkey(0)
            cut = cut.convert_alpha()
            cut.blit(image, (0, 0), pygame.Rect(x, y, sprite_width, sprite_height))
            cut_images.append(cut)

    return cut_images