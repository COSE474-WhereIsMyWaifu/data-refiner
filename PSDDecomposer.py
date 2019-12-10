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
    

def convert_psd(psd_dir, output_dir, output_title):
    json_arr = []
    try:
        os.mkdir(output_dir + output_title + '/')
    except:
        pass

    for file in os.listdir('./' + psd_dir):
        if fnmatch.fnmatch(file, '*.psd'):
            psdfile_path = psd_dir + file
            title = file[0:len(file) - 4]
            output_sub = output_title + '/' + title + '/'
            print('converting : ', psdfile_path)
            print('to : ', output_dir + output_sub)

            try:
                os.mkdir(output_dir + output_sub)
            except:
                pass

                
            # json object to build
            json_obj = {}
            json_obj['segmented'] = False
            json_obj['title'] = title
            json_obj['faces'] = {}
            
            psd = PSDImage.open(psdfile_path)
            for layer in psd:
                layer.visible = True
                layer_img = layer.topil()
                
                properties = layer.name.split('_')

                if len(properties) == 1:
                    # save background
                    saving_path = output_sub + 'background.png'
                    json_obj['background_path'] = saving_path
                    layer_img.save(output_dir + saving_path)
                    
                else:
                    # name for this layer
                    
                    # parse property of layer
                    if properties[0] not in json_obj['faces']:
                        json_obj['faces'][properties[0]] = {}
                    json_obj['faces'][properties[0]][properties[1]] = {}
                    
                    # save and build json
                    if len(properties) == 2:
                        saving_path = output_sub + layer.name
                        json_obj['faces'][properties[0]][properties[1]]['path'] = saving_path + '.png'
                        json_obj['faces'][properties[0]][properties[1]]['mask'] = saving_path + '_mask.png'
                        json_obj['faces'][properties[0]][properties[1]]['bbox'] = layer.bbox
                        json_obj['segmented'] = True
                        
                        layer_img.save(output_dir + saving_path + '.png')
                        mask_img = to_mask(layer_img)
                        plt.imsave(output_dir + saving_path + '_mask.png', mask_img, cmap='gray')

                    if len(properties) == 3:
                        saving_path = output_sub + properties[0] + '_' + properties[1]
                        json_obj['faces'][properties[0]][properties[1]]['kind'] = properties[2]
                        json_obj['faces'][properties[0]][properties[1]]['path'] = saving_path + '.png'
                        json_obj['faces'][properties[0]][properties[1]]['bbox'] = layer.bbox
                        layer_img.save(output_dir + saving_path + '.png')
                        
                    
            json_arr.append(json_obj)
    with open(output_dir + output_title + '.json', 'w') as outfile:
        json.dump(json_arr, outfile, indent=4)



# In[3]:

def is_valid_emote(emote):
    emote_list = ['happy', 'sadness', 'neutral', 'fear', 'angry',
                  'contempt', 'happiness', 'disgust', 'surprise', 'anger', 
                  'suprise', 'sad', 'ashamed', 'fearness', 'neutral', 
                  'unavailable', 'small', 'shame']
    
    emotes = emote.split(',')
    
    for e in emotes:
        split_e = e.split('|')
        
        if len(split_e) == 1:
            if split_e[0] not in emote_list:
                return False
        elif len(split_e) == 2:
            if split_e[0] not in emote_list:
                return False
            try:
                float(split_e[1])
            except ValueError:
                return False
        else:
            return False

    return True

def validate_json(json_file_name):
    with open(json_file_name, 'rb') as in_file:
        json_arr = json.load(in_file)
    
    prop_list = ['hair', 'eyeL', 'eyeR', 'emote']
    
    valid = True
    for pic in json_arr:
        if 'title' not in pic:
            print('pic with no title on \'' + json_file_name + '\'')
            continue
        if 'background_path' not in pic:
            print(str(pic['title'])  + ' : key \'background_path\' not found')
            continue
        if 'faces' not in pic:
            print(str(pic['title'])  + ' : key \'faces\' not found')
            continue
            
        if len(pic['faces']) == 0:
            print(str(pic['title'])  + ' : no items in key \'faces\'')
            continue
            
        for face_key in pic['faces']:
            if 'emote' not in pic['faces'][face_key]:
                print(str(pic['title']) + ' : ' + str(face_key) + ' : key \'emote\' not found')
                continue
            
            for prop_key in pic['faces'][face_key]:
                if prop_key not in prop_list:
                    print(str(pic['title']) + ' : ' + str(face_key) + ' : \'' + str(prop_key) + '\' is not a valid property key')
                    continue
                    
                if prop_key != 'emote':
                    if 'path' not in pic['faces'][face_key][prop_key]:
                        print(str(pic['title']) + ' : ' + str(face_key) + 
                              ' : ' + str(prop_key) + ' : no items in key \'path\'')
                        continue
                    if 'mask' not in pic['faces'][face_key][prop_key]:
                        print(str(pic['title']) + ' : ' + str(face_key) + 
                              ' : ' + str(prop_key) + ' : no items in key \'mask\'')
                        continue
                    if 'bbox' not in pic['faces'][face_key][prop_key]:
                        print(str(pic['title']) + ' : ' + str(face_key) + 
                              ' : ' + str(prop_key) + ' : no items in key \'bbox\'')
                        continue
                elif prop_key == 'emote':
                    if 'path' not in pic['faces'][face_key][prop_key]:
                        print(str(pic['title']) + ' : ' + str(face_key) + 
                              ' : ' + str(prop_key) + ' : no items in key \'path\'')
                        continue
                    if 'kind' not in pic['faces'][face_key][prop_key]:
                        print(str(pic['title']) + ' : ' + str(face_key) + 
                              ' : ' + str(prop_key) + ' : no items in key \'kind\'')
                        continue
                    if 'bbox' not in pic['faces'][face_key][prop_key]:
                        print(str(pic['title']) + ' : ' + str(face_key) + 
                              ' : ' + str(prop_key) + ' : no items in key \'bbox\'')
                        continue
                        
                    if is_valid_emote(pic['faces'][face_key][prop_key]['kind']) is False:
                        print(str(pic['title']) + ' : ' + str(face_key) + 
                              ' : ' + str(prop_key) + ' : \'' + str(pic['faces'][face_key][prop_key]['kind']) + 
                              '\' is not a valid property key')
                        continue
                    
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
    
def show_json(target_json, image_dir, plot_emote = True, plot_segment = True):
    
    with open(target_json, 'rb') as infile:
        json_arr = json.load(infile)
        
    for pic in json_arr:
        background_path = image_dir + pic['background_path']
        
        for face_key in pic['faces']:
            for prop_key in pic['faces'][face_key]:
                print('------------------------------------------------------------------------------')
                print(pic['title'] + " " + face_key + " " + prop_key)
                if prop_key != 'emote' and plot_segment is True:
                    bbox = pic['faces'][face_key][prop_key]['bbox']
                    original_path = image_dir + pic['faces'][face_key][prop_key]['path']
                    mask_path = image_dir + pic['faces'][face_key][prop_key]['mask']
                    show_imgmask(background_path, bbox, original_path, mask_path)
                elif prop_key == 'emote' and plot_emote is True:
                    print('emote = ' + pic['faces'][face_key][prop_key]['kind'])
                    
                    bbox = pic['faces'][face_key][prop_key]['bbox']
                    original_path = image_dir + pic['faces'][face_key][prop_key]['path']
                    show_emote(background_path, bbox, original_path)
       
    
import sys
if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print('more parameters needed\n')
    else:
        input_dir = str(sys.argv[1])
        
        title_list = os.listdir(input_dir)
        
        for title in title_list:
            target = '../data/orig/' + title + '/'
            output_dir = '../data/refined/'
            output_title = title
    
            convert_psd(target, output_dir, output_title)
            validate_json(output_dir + title + '.json')
    