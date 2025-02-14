from os import listdir, mkdir
from os.path import join, isfile, exists
import cv2
import tempfile
from typing import List
from tqdm import tqdm
import numpy as np
import imageio


def animate_multiple_streams(folders_list: List, prefix: str = None, save_path: str = None, nrows: int = None,
                             ncols: int = None, fps: int = 30):
    DEFAULT_NCOLS = 3

    # Getting the number of folders to merge
    num_streams = len(folders_list)

    assert num_streams > 0
    if (nrows is None and ncols is not None) or (nrows is not None and ncols is None):
        raise ValueError('Both nrows and ncols needs to be specified')
    if ncols is not None and nrows is not None and num_streams > (nrows * ncols):
        raise ValueError('Requested nrows and ncols don\'t match the number of input streams')

    num_imgs = None
    for f in folders_list:
        num_imgs_in_folder = listdir(f)
        if num_imgs is None:
            num_imgs = num_imgs_in_folder
        else:
            # Making sure all folders have the same number of images
            assert num_imgs == num_imgs_in_folder

    if nrows is None or ncols is None:
        nrows = num_streams // DEFAULT_NCOLS + 1
        ncols = max(num_streams % DEFAULT_NCOLS, DEFAULT_NCOLS)

    # Get the first image to determine dimensions
    files = sorted([f for f in listdir(folders_list[0]) if isfile(join(folders_list[0], f))])
    first_image = cv2.imread(join(folders_list[0], files[0]))
    height, width, _ = first_image.shape
    output_height, output_width = height * nrows, width * ncols

    # Creating the output canvas
    image_list = []
    with tempfile.TemporaryDirectory() as tmpdirname:
        output_canvas = np.zeros((output_height, output_width, 3))
        for filename in tqdm(files, desc='Preparing output video frames...'):
            for idx, folder in enumerate(folders_list):
                img = cv2.imread(join(folder, filename))
                idx_y = idx // ncols
                idx_x = idx % ncols
                output_canvas[(idx_y * height):((idx_y + 1) * height), (idx_x * width):((idx_x + 1) * width)] = img
            frame_filenname = join(tmpdirname, f'merged_{filename}')
            image_list.append(frame_filenname)
            cv2.imwrite(frame_filenname, output_canvas)

        # Define the codec and create VideoWriter object
        save_path = './output' if save_path is None else save_path
        if not exists(save_path):
            mkdir(save_path)

        video_name = join(save_path, 'merged.avi' if prefix is None else f'{prefix}_merged.avi')
        with imageio.v2.get_writer(video_name, fps=fps) as video:
            for image_path in tqdm(image_list, desc='Creating output video...'):
                frame = imageio.v2.imread(image_path)
                video.append_data(frame)


streams = ['/media/blink/12TB_HDD/gen.ai/face.dancer/output/20230331-123918-C8C66CB2',
           '/media/blink/12TB_HDD/gen.ai/face.dancer/output/20230331-123918-C8C66CB2_asian',
           '/media/blink/12TB_HDD/gen.ai/face.dancer/output/20230331-123918-C8C66CB2_black']
animate_multiple_streams(streams,
                         save_path='/media/blink/12TB_HDD/gen.ai/face.dancer/output',
                         prefix='testing_merge')