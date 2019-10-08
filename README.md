# data-refiner
This converts psd files to multiple png images and json  


## psd file
layer name should be one of these :  
    background : channel = 3  
    (id)_(hair|eyeR|eyeL)  
    (id)_emote_(happy|sadness|surprise|disgust|fear|angry|neutral|contempt)  


## png files
each layer in folder_name/file_name.psd file is converted as :  
    folder_name/file_name/layer_name.png  

explicitly, background image, which has 3 channel is converted to :  
    folder_name/file_name/file_name.png  


## json file

```json
[
    {
        "title": "(file_name)",
        "faces": {
            "(id)" : {
                "emote" : {
                    "kind": "(happy|sadness|surprise|disgust|fear|angry|neutral|contempt)",
                    "path": "./(folder_name)/(file_name)/(layer_name).png",
                    "bbox": ["xmin", "ymin", "xmax", "ymax"]
                },
                
                "(hair|eyeR|eyeL)": {
                    "path": "./(folder_name)/(file_name)/(layer_name).png",
                    "mask": "./(folder_name)/(file_name)/(layer_name)_mask.png",
                    "bbox": ["xmin", "ymin", "xmax", "ymax"]
                },
            },
            
        }
    }
]
```










