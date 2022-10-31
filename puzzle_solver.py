import numpy as np
import matplotlib.pyplot as plt
import os

# from sklearn.metrics import mean_squared_error

from scipy import ndimage

from skimage.transform import rescale, resize

from skimage.metrics import hausdorff_distance, normalized_mutual_information, mean_squared_error

import tqdm

from skimage.color import rgb2gray

puzzle_path = r'/home/s-sd/Desktop/puzzle_solver'

img_orig = plt.imread(os.path.join(puzzle_path, 'puzzle_pic_1.jpg'))
# img = np.expand_dims(rgb2gray(img_orig), axis=-1)
img = img_orig

piece_size = 35

num_sim_to_use = 5

num_channels = 3

from tiler import Tiler

tiler = Tiler(
    data_shape=img.shape,
    tile_shape=(piece_size, piece_size, num_channels),
    overlap=(0, 0, 0),
    channel_dimension=2,
)

tiles = []

for tile_id, tile in tiler(img, progress_bar=True):
    tiles.append(tile)

piece_loaded = plt.imread(os.path.join(puzzle_path, 'piece_3.jpg'))
# piece_loaded = np.expand_dims(rgb2gray(piece_loaded), axis=-1)

piece_000 = piece_loaded
piece_090 = ndimage.rotate(piece_000, 90)
piece_180 = ndimage.rotate(piece_000, 180)
piece_270 = ndimage.rotate(piece_000, 270)


def MSE(Y, YH):
    return np.square(Y - YH).mean()

from copy import deepcopy

errors = np.zeros((len(tiles), 4))

for piece_ind, piece in enumerate([piece_000, piece_090, piece_180, piece_270]):
    for i, tile in tqdm.tqdm(enumerate(tiles)):
        piece = resize(piece, (piece_size, piece_size, num_channels))
        tile = resize(tile, (piece_size, piece_size, num_channels))
        hd = hausdorff_distance(piece, tile)
        mse = mean_squared_error(piece, tile)
        nmi = normalized_mutual_information(piece, tile)
        errors[i, piece_ind] = 0.8*mse + 0.1*hd + 0.1*nmi

sorted_inds = np.argsort(errors, axis=0)

pred_tile_loc = []

for num in range(num_sim_to_use):
    for rot in range(4):
        min_loc = np.where(sorted_inds[:, rot]==num)[0][0]
        pred_tile_loc.append(min_loc)

pred_tile = np.mean(pred_tile_loc)

total_tiles = len(tiles)

pred_tile_loc_i = int(np.floor((piece_size*pred_tile) % img.shape[1]))
pred_tile_loc_j = int(np.floor(((piece_size*pred_tile) / img.shape[1]) * piece_size))

# img[pred_tile_loc_j, pred_tile_loc_i]

import matplotlib.pyplot as plt
import matplotlib.patches as ptch

fig, ax = plt.subplots()

img_copy = deepcopy(img_orig)

ax.imshow(img_copy)

rect = ptch.Rectangle((pred_tile_loc_i, pred_tile_loc_j), 40, 40, linewidth=2.5, edgecolor='k', facecolor='none')

ax.add_patch(rect)

# rr, cc = draw.circle_perimeter(pred_tile_loc_j, pred_tile_loc_i, 2)
# img_copy[rr, cc] = [0, 255, 0]
# plt.imshow(img_copy)


