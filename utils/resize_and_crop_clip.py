from moviepy.editor import vfx

def resize_and_crop_clip(clip, size=(720, 1280)):
    aspect_ratio = clip.size[0] / clip.size[1]
    target_aspect_ratio = size[0] / size[1]

    if aspect_ratio > target_aspect_ratio:  # landscape aspect ratio
        new_width = int(clip.size[1] * target_aspect_ratio)
        new_height = clip.size[1]
    else:  # portrait aspect ratio
        new_width = clip.size[0]
        new_height = int(clip.size[0] / target_aspect_ratio)

    crop_x = (clip.size[0] - new_width) // 2
    crop_y = (clip.size[1] - new_height) // 2

    cropped_clip = clip.crop(
        x1=crop_x, y1=crop_y, x2=crop_x + new_width, y2=crop_y + new_height)
    return cropped_clip.fx(vfx.resize, width=size[0], height=size[1])
