import os.path
import random
import time
from os.path import dirname, exists, join
from ovos_bus_client.message import Message
from ovos_bus_client.session import SessionManager, Session
from ovos_utils import classproperty
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
        self.sess2cam = {}
        if "play_sound" not in self.settings:
            self.settings["play_sound"] = True
        self.add_event("ovos.phal.camera.pong", self.handle_pong)
        self.bus.emit(Message("ovos.phal.camera.ping"))

    def handle_pong(self, message: Message):
        sess = SessionManager.get(message)
        self.sess2cam[sess.session_id] = True

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

    @intent_handler("have_camera.intent")
    def handle_camera_check(self, message):
        sess = SessionManager.get(message)
        if not self.sess2cam.get(sess.session_id):
            self.speak_dialog("camera_error")
        else:
            self.speak_dialog("camera_yes")

    @intent_handler("take_picture.intent")
    def handle_take_picture(self, message):
        sess = SessionManager.get(message)
        if not self.sess2cam.get(sess.session_id):
            self.speak_dialog("camera_error")
            return

        self.speak_dialog("get_ready", wait=True)
        # need time to Allow sensor to stabilize
        self.gui.show_text("3")
        self.speak("3", wait=True)
        self.gui.show_text("2")
        self.speak("2", wait=True)
        self.gui.show_text("1")
        self.speak("1", wait=True)

        pic_path = join(self.pictures_folder, time.strftime("%Y-%m-%d_%H-%M-%S") + ".jpg")
        self.bus.emit(message.forward("ovos.phal.camera.get", {"path": pic_path}))

        self.play_camera_sound()

        self.gui.clear()
        self.gui.show_image(pic_path)
        if random.choice([True, False]):
            self.speak_dialog("picture")
