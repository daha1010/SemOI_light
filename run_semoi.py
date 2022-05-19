#!/usr/bin/env python3
#
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Camera image classification demo code.

Runs continuous image classification on camera frames and prints detected object
classes.

Example:
image_classification_camera.py --num_frames 10
"""
import argparse
import contextlib

from aiy.vision.inference import CameraInference
from aiy.vision.models import image_classification
from picamera import PiCamera

from aiy.leds import Leds, Color
from gpiozero import Button

from object_classification_for_pi import run_semantic

import picamera
from PIL import Image
from aiy.vision.inference import ImageInference


def classes_info(classes):
    return ', '.join('%s (%.2f)' % pair for pair in classes)


def crop_center(image):
    width, height = image.size
    size = min(width, height)
    x, y = (width - size) / 2, (height - size) / 2
    return image.crop((x, y, x + size, y + size)), (x, y)


with picamera.PiCamera() as camera:
    camera.resolution = (3280, 2464) # initializing camera and button
    button = Button(23)
    with Leds() as leds:
        while True:
            with ImageInference(image_classification.model()) as inference:
                #button = Button(23)
                leds.update(Leds.rgb_on(Color.GREEN)) # system is ready
                print("press button to analyze")
                button.wait_for_press()
                camera.capture("class_pic.jpg")
                leds.update(Leds.rgb_on(Color.YELLOW))  # in progress
                image = Image.open("class_pic.jpg")
                image_center, offset = crop_center(image)

                result = inference.run(image_center)
                #leds.update(Leds.rgb_on(Color.GREEN))
                print("inference is running")
                #button.wait_for_press()
                #leds.update(Leds.rgb_on(Color.YELLOW))
                detected_classes = [] # contains classification results
                # print("Ergebnisse: " + str(result))
                classes = image_classification.get_classes(result, top_k=5) # classifies top 5 classes
                detected_classes.append(classes_info(classes))
                print("Classification results: " + str(detected_classes))
                # print(classes_info(classes))
                semantic_augmentation = run_semantic(detected_classes) # runs semantic
                print("Semantic augmentation: " + str(semantic_augmentation))
                if classes:
                    camera.annotate_text = '%s (%.2f)' % classes[0]
            leds.update(Leds.rgb_off())
