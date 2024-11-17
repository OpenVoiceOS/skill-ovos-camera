import os.path
import platform
import subprocess
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

try:
    from picamera2 import Picamera2
except ImportError:
    Picamera2 = None


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
        self._camera = None
        self.camera_type = self.detect_camera_type()

    @staticmethod
    def detect_camera_type():
        """Detect if running on Raspberry Pi with libcamera or desktop."""
        if platform.system() == "Linux":
            # Check if running on Raspberry Pi
            if "Raspberry Pi" in platform.uname().machine:
                # Check if libcamera is available
                try:
                    result = subprocess.run(["which", "libcamera-still"],
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            check=True)
                    if result.stdout:
                        return "libcamera"
                except subprocess.CalledProcessError:
                    LOG.warning("libcamera not found, falling back to OpenCV")
            return "opencv"
        else:
            return "opencv"

    def open_camera(self):
        """Open camera based on detected type."""
        if self.camera_type == "libcamera":
            if Picamera2 is None:
                LOG.error("Picamera2 library is not installed")
                return None
            try:
                self._camera = Picamera2()
                self._camera.start()
                LOG.info("libcamera initialized")
            except Exception as e:
                LOG.error(f"Failed to start libcamera: {e}")
                return None
        elif self.camera_type == "opencv":
            try:
                self._camera = VideoStream(self.settings.get("video_source", 0))
                if not self._camera.stream.grabbed:
                    self._camera = None
                    raise ValueError("OpenCV Camera stream could not be started")
                self._camera.start()
            except Exception as e:
                LOG.error(f"Failed to start OpenCV camera: {e}")
                return None
        return self._camera

    def get_frame(self, cam) -> np.ndarray:
        if self.camera_type == "libcamera":
            return cam.capture_array()
        else:
            return cam.get()

    def close_camera(self):
        """Close the camera."""
        if self._camera:
            if self.camera_type == "libcamera":
                self._camera.close()
            elif self.camera_type == "opencv":
                self._camera.stop()
            self._camera = None

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
        cam = self.open_camera()
        if cam is None:
            self.speak_dialog("camera_error")
            return
        self.play_camera_sound()
        frame = self.get_frame(cam)
        pic_path = join(self.pictures_folder, time.strftime("%Y-%m-%d_%H-%M-%S") + ".jpg")
        cv2.imwrite(pic_path, frame)
        self.gui.show_image(pic_path)
        self.speak_dialog("picture")
        if not self.settings.get("keep_camera_open"):
            self.close_camera()

    def shutdown(self):
        self.close_camera()
