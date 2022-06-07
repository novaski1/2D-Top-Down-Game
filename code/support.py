import pygame
from csv import reader
from os import walk
from settings import *

def import_csv_layout(path):
    terrain_map = []
    with open(path) as level_map:
        layout = reader(level_map,delimiter=',')
        for row in layout:
            terrain_map.append(list(row))
    
        return(terrain_map)

def import_folder(path):
    surface_list = []
    for _,__,img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            image_surf = pygame.transform.scale(image_surf,(image_surf.get_width()*4, image_surf.get_height()*4))
            surface_list.append(image_surf)
    
    return surface_list

def chunk_loading(path):
    terrain_map = [[] for x in range(N_CHUNKS)]
    for i in range(N_CHUNKS-1):
        for j in range(N_CHUNKS-1):
            chunk_no = str('[' + str(i) + ';' + str(j) + ']')
            chunk_img = pygame.image.load(str(path + chunk_no + '.png')).convert()
            chunk_img = pygame.transform.scale(chunk_img,(chunk_img.get_height()*4,chunk_img.get_width()*4))

            terrain_map[i].append(chunk_img)
    
    return(terrain_map)

