from collections import namedtuple
from functools import partial

import cv2 as cv

import constants as const
import utils

Trackbar = namedtuple('Trackbar',
                      ['name', 'prop', 'default_value', 'max_value', 'min_value'],
                      defaults=[0])


def set_param(trackbar: Trackbar, value):
    for cam in [cam1, cam2]:
        cam.set(trackbar.prop, trackbar.min_value + value)


map1_1, map1_2, map2_1, map2_2 = utils.load_stereo_maps(const.CALIB_OUTPUT_FILE)

trackbars = [Trackbar('focus', cv.CAP_PROP_FOCUS, 0, 1023),
             Trackbar('exposure', cv.CAP_PROP_EXPOSURE, 430, 625, 2),
             Trackbar('brightness', cv.CAP_PROP_BRIGHTNESS, 128, 255),
             Trackbar('contrast', cv.CAP_PROP_CONTRAST, 45, 255),
             Trackbar('gamma', cv.CAP_PROP_GAMMA, 150, 150, 90),
             ]

WINNAME = 'preview'
cv.namedWindow(WINNAME)
cv.resizeWindow(WINNAME, const.WIN_SIZE[0] * 2, const.WIN_SIZE[1] * 2)

for trackbar in trackbars:
    cv.createTrackbar(trackbar.name, WINNAME, trackbar.default_value,
                      trackbar.max_value - trackbar.min_value,
                      partial(set_param, trackbar=trackbar))

cam1 = cv.VideoCapture(const.CAM1_ID)
cam2 = cv.VideoCapture(const.CAM2_ID)

for cam in (cam1, cam2):
    cam.set(cv.CAP_PROP_FOURCC, cv.VideoWriter.fourcc('M', 'J', 'P', 'G'))
    cam.set(cv.CAP_PROP_AUTOFOCUS, 0)
    cam.set(cv.CAP_PROP_AUTO_EXPOSURE, 1)

utils.set_img_size((cam1, cam2), const.IMG_SIZE)

while True:
    if cam1.grab() and cam2.grab():
        img1 = cam1.retrieve()[1]
        img2 = cam2.retrieve()[1]
        if const.ROTATE_CAM1 is not None:
            img1 = cv.rotate(img1, const.ROTATE_CAM1)
        if const.ROTATE_CAM2 is not None:
            img2 = cv.rotate(img2, const.ROTATE_CAM2)
        img1 = cv.remap(img1,
                        map1_1, map1_2,
                        cv.INTER_LINEAR)
        img2 = cv.remap(img2,
                        map2_1, map2_2,
                        cv.INTER_LINEAR)
        preview = cv.hconcat([img1, img2])
        cv.imshow(WINNAME, preview)
    if cv.waitKey(1) != -1:
        break

cv.destroyAllWindows()
cam1.release()
cam2.release()
