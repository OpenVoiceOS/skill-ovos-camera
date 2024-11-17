import os.path
import time
from os.path import dirname, exists, join

import cv2
from imutils.video import VideoStream
from ovos_utils import classproperty
from ovos_utils.log import LOG
from ovos_utils.process_utils import RuntimeRequirements

from ovos_workshop.decorators import intent_handler
from ovos_workshop.skills import OVOSSkill


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

    def open_camera(self) -> VideoStream:
        if self._camera is None:
            try:
                LOG.info("initializing camera stream")
                self._camera = VideoStream(self.settings.get("video_source", 0))
                if not self._camera.stream.grabbed:
                    self._camera = None
                    raise ValueError("Camera stream could not be started")
                self._camera.start()
            except Exception as e:
                LOG.error(f"Failed to open camera: {e}")
                return None
        return self._camera

    def close_camera(self):
        if self._camera:
            LOG.info("closing camera stream")
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
        frame = cam.get().copy()
        pic_path = join(self.pictures_folder, time.strftime("%Y-%m-%d_%H-%M-%S") + ".jpg")
        cv2.imwrite(pic_path, frame)
        self.speak_dialog("picture")
        if not self.settings.get("keep_camera_open"):
            self.close_camera()

    def shutdown(self):
        self.close_camera()
