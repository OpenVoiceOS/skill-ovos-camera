import os.path
import random
import time
from os.path import dirname, exists, join

import cv2
import numpy as np
from imutils.video import VideoStream
from ovos_utils import classproperty
from ovos_utils.log import LOG
from ovos_utils.process_utils import RuntimeRequirements

from ovos_workshop.decorators import intent_handler
from ovos_workshop.skills import OVOSSkill


class Camera:
    # TODO - move to a PHAL plugin so camera
    #  can be shared across components
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self._camera = None
        self.camera_type = self.detect_camera_type()

    @staticmethod
    def detect_camera_type() -> str:
        """Detect if running on Raspberry Pi with libcamera or desktop."""
        try:
            # only works in rpi
            import libcamera
            return "libcamera"
        except:
            return "opencv"

    def open(self):
        """Open camera based on detected type."""
        if self.camera_type == "libcamera":
            try:
                from picamera2 import Picamera2
                self._camera = Picamera2()
                self._camera.start()
                LOG.info("libcamera initialized")
            except Exception as e:
                LOG.error(f"Failed to start libcamera: {e}")
                return None
        elif self.camera_type == "opencv":
            try:
                self._camera = VideoStream(self.camera_index)
                if not self._camera.stream.grabbed:
                    self._camera = None
                    raise ValueError("OpenCV Camera stream could not be started")
                self._camera.start()
            except Exception as e:
                LOG.error(f"Failed to start OpenCV camera: {e}")
                return None
        return self._camera

    def get_frame(self) -> np.ndarray:
        if self.camera_type == "libcamera":
            return self._camera.capture_array()
        else:
            return self._camera.get()

    def close(self):
        """Close the camera."""
        if self._camera:
            if self.camera_type == "libcamera":
                self._camera.close()
            elif self.camera_type == "opencv":
                self._camera.stop()
            self._camera = None

    def __enter__(self):
        """Enter the context and open the camera."""
        if self.open() is None:
            raise RuntimeError("Failed to open the camera")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the context and close the camera."""
        self.close()


class WebcamSkill(OVOSSkill):

    @classproperty
    def runtime_requirements(self):
        return RuntimeRequirements(internet_before_load=False,
                                   network_before_load=False,
                                   gui_before_load=False,
                                   requires_internet=False,
                                   requires_network=False,
                                   requires_gui=False,
                                   no_internet_fallback=True,
                                   no_network_fallback=True,
                                   no_gui_fallback=True)

    def initialize(self):
        if "video_source" not in self.settings:
            self.settings["video_source"] = 0
        if "play_sound" not in self.settings:
            self.settings["play_sound"] = True
        self.camera = Camera(self.settings.get("video_source", 0))

    @property
    def pictures_folder(self) -> str:
        folder = os.path.expanduser(self.settings.get("pictures_folder", "~/Pictures"))
        os.makedirs(folder, exist_ok=True)
        return folder

    def play_camera_sound(self):
        if self.settings["play_sound"]:
            s = self.settings.get("camera_sound_path") or \
                join(dirname(__file__), "camera.wav")
            if exists(s):
                self.play_audio(s, instant=True)

    @intent_handler("take_picture.intent")
    def handle_take_picture(self, message):
        try:
            with self.camera as cam:
                self.speak_dialog("get_ready", wait=True)
                # need time to Allow sensor to stabilize
                self.gui.show_text("3")
                self.speak("3", wait=True)
                self.gui.show_text("2")
                self.speak("2", wait=True)
                self.gui.show_text("1")
                self.speak("1", wait=True)
                self.play_camera_sound()
                self.gui.clear()
                frame = self.camera.get_frame()
                pic_path = join(self.pictures_folder, time.strftime("%Y-%m-%d_%H-%M-%S") + ".jpg")
                cv2.imwrite(pic_path, frame)
                self.gui.show_image(pic_path)
                if random.choice([True, False]):
                    self.speak_dialog("picture")
        except RuntimeError as e:
            LOG.error(e)
            self.speak_dialog("camera_error")

    def shutdown(self):
        # just in case
        self.camera.close()
