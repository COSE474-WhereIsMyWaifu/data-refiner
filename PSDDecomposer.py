#!/usr/bin/env python
# coding: utf-8

# In[1]:


import psd_tools
from psd_tools import PSDImage
from PIL import Image

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as patches

import os
import fnmatch
import json


# In[2]:


def to_mask(img):
    mask = np.array(img)
    mask = np.clip(mask[:,:,3::4], 0, 1) * 255
    mask = mask.reshape(img.height, img.width)

    return mask
    

def convert_psd(anime_folder):
    json_arr = []
    for file in os.listdir('./' + anime_folder):
        if fnmatch.fnmatch(file, '*.psd'):
            file_path = './' + anime_folder + '/' + file
            folder_path = file_path[0:len(file_path) - 4]
            print('converting : ', file_path)
        
            try:
                os.mkdir(folder_path)
            except:
                print('folder : ', folder_path, ' already exist')
                
            # json object to build
            json_obj = {}
            json_obj['title'] = file[0:len(file) - 4]
            json_obj['faces'] = {}
            
            psd = PSDImage.open(file_path)
            for layer in psd:
                layer.visible = True
                layer_img = layer.topil()
                channel = len(layer_img.getbands())
                
                if channel == 3:
                    # save background
                    saving_path = folder_path + '/' + file[0:len(file) - 4] + '.png'
                    json_obj['background_path'] = saving_path
                    layer_img.save(saving_path)
                    
                elif channel == 4:
                    # name for this layer
                    saving_path = folder_path + '/' + layer.name
                    
                    # parse property of layer
                    properties = layer.name.split('_')
                    if properties[0] not in json_obj['faces']:
                        json_obj['faces'][properties[0]] = {}
                    json_obj['faces'][properties[0]][properties[1]] = {}
                    
                    # save and build json
                    if len(properties) == 2:
                        json_obj['faces'][properties[0]][properties[1]]['path'] = saving_path + '.png'
                        json_obj['faces'][properties[0]][properties[1]]['mask'] = saving_path + '_mask.png'
                        json_obj['faces'][properties[0]][properties[1]]['bbox'] = layer.bbox
                        
                        mask_img = to_mask(layer_img)
                        layer_img.save(saving_path + '.png')
                        plt.imsave(saving_path + '_mask.png', mask_img, cmap='gray')
                    if len(properties) == 3:
                        json_obj['faces'][properties[0]][properties[1]]['kind'] = properties[2]
                        json_obj['faces'][properties[0]][properties[1]]['path'] = saving_path + '.png'
                        json_obj['faces'][properties[0]][properties[1]]['bbox'] = layer.bbox
                        layer_img.save(saving_path + '.png')
                        
                    
            json_arr.append(json_obj)
    with open(anime_folder + '.json', 'w') as outfile:
        json.dump(json_arr, outfile, indent=4)



# In[3]:


def validate_json(target_json):
    with open(target_json, 'rb') as infile:
        json_arr = json.load(infile)
    
    emote_list = ['happy', 'sadness', 'neutral', 'fear', 'angry', 'contempt', 'disgust', 'surprise']
    valid = True
    for pic in json_arr:
        assert 'background_path' in pic
        assert 'faces' in pic
        assert 'title' in pic
        
        for face_key in pic['faces']:
            assert 'emote' in pic['faces'][face_key]
            assert 'hair' in pic['faces'][face_key]
            
            for prop_key in pic['faces'][face_key]:
                if prop_key != 'emote':
                    assert 'path' in pic['faces'][face_key][prop_key]
                    assert 'mask' in pic['faces'][face_key][prop_key]
                    assert 'bbox' in pic['faces'][face_key][prop_key]
                elif prop_key == 'emote':
                    assert 'path' in pic['faces'][face_key][prop_key]
                    assert 'kind' in pic['faces'][face_key][prop_key]
                    assert 'bbox' in pic['faces'][face_key][prop_key]
                    assert pic['faces'][face_key][prop_key]['kind'] in emote_list
                    
        print(pic['title'], ' is valid')
                    
    return valid
    
    


# In[4]:


def show_imgmask(background_path, bbox, original_path, mask_path):
    _, ax = plt.subplots(1, 3, figsize=(14, 14))
    
    background_img = mpimg.imread(background_path)
    original_img = mpimg.imread(original_path)
    mask_img = mpimg.imread(mask_path)
    bounding = patches.Rectangle((bbox[0],bbox[1]), bbox[2] - bbox[0], bbox[3] - bbox[1], 
                                 linewidth=1, edgecolor='r', facecolor='none')
    
    ax[0].imshow(background_img)
    ax[0].add_patch(bounding)
    ax[1].imshow(original_img)
    ax[2].imshow(mask_img)
    
    plt.tight_layout()
    plt.show()
    
def show_emote(background_path, bbox, emote_path):
    _, ax = plt.subplots(1, 2, figsize=(14, 14))
    
    background_img = mpimg.imread(background_path)
    emote_img = mpimg.imread(emote_path)
    bounding = patches.Rectangle((bbox[0],bbox[1]), bbox[2] - bbox[0], bbox[3] - bbox[1], 
                                 linewidth=1, edgecolor='r', facecolor='none')
    
    ax[0].imshow(background_img)
    ax[0].add_patch(bounding)
    ax[1].imshow(emote_img)
    
    plt.tight_layout()
    plt.show()
    
def show_json(target_json):
    
    with open(target_json, 'rb') as infile:
        json_arr = json.load(infile)
        
    for pic in json_arr:
        background_path = pic['background_path']
        
        for face_key in pic['faces']:
            for prop_key in pic['faces'][face_key]:
                print('------------------------------------------------------------------------------')
                print(pic['title'] + " " + face_key + " " + prop_key)
                if prop_key != 'emote':
                    bbox = pic['faces'][face_key][prop_key]['bbox']
                    original_path = pic['faces'][face_key][prop_key]['path']
                    mask_path = pic['faces'][face_key][prop_key]['mask']
                    show_imgmask(background_path, bbox, original_path, mask_path)
                elif prop_key == 'emote':
                    print('emote = ' + pic['faces'][face_key][prop_key]['kind'])
                    
                    bbox = pic['faces'][face_key][prop_key]['bbox']
                    original_path = pic['faces'][face_key][prop_key]['path']
                    show_emote(background_path, bbox, original_path)
                
            
    