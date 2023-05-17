import time
from os import makedirs
from os.path import dirname, exists, expanduser, join

import cv2
from ovos_utils.log import LOG
from ovos_workshop.decorators import intent_handler
from ovos_workshop.skills import OVOSSkill
from shared_camera import ZMQCamera


class WebcamSkill(OVOSSkill):

    def initialize(self):
        LOG.info("initializing videostream")

        if "video_source" not in self.settings:
            self.settings["video_source"] = 0
        if "play_sound" not in self.settings:
            self.settings["play_sound"] = True
        if "picture_path" not in self.settings:
            self.settings["picture_path"] = "~/Photos"

        makedirs(self.settings["picture_path"], exist_ok=True)

        self.camera = ZMQCamera(camera_index=self.settings["video_source"])
        self.last_timestamp = 0
        self.add_event("webcam.request", self.handle_get_picture)

    @property
    def last_frame(self):
        self.last_timestamp = time.time()
        if self.camera:
            return self.camera.get().copy()
        return None

    @intent_handler("take_picture.intent")
    def handle_take_picture(self, message):

        if self.settings["play_sound"]:
            s = self.settings.get("camera_sound_path") or \
                join(dirname(__file__), "camera.wav")
            if exists(s):
                self.play_audio(s)

        pic_path = expanduser(join(self.settings["picture_path"], time.asctime() + ".jpg"))
        cv2.imwrite(pic_path, self.last_frame)
        self.speak_dialog("picture")

    def handle_get_picture(self, message):
        # TODO - skill_api
        path = join(self.settings["picture_path"], time.asctime() + ".jpg")
        cv2.imwrite(path, self.last_frame)
        self.bus.emit(message.reply("webcam.picture", {"path": path}))

    def shutdown(self):
        self.camera.stop_stream()
        self.camera.shutdown()
        super(WebcamSkill, self).shutdown()
