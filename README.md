## Camera skill

[shared camera](https://github.com/NeonGeckoCom/shared_camera) for OpenVoiceOS

this skill is WIP! you most likely want to use https://github.com/OpenVoiceOS/skill-ovos-qml-camera instead   (depends on mycroft-gui)


TODO

- PHAL plugin for the actual shared camera implementation
- skill becomes a VUI + UI specifically for taking pictures
- new ovos_workshop skill class for VisionSkill, exposing a live feed (numpy array) property

## Description

take pictures, share a camera stream across OpenVoiceOS

- local
- zmq
- redis

## Examples

* "take a picture"


## Using webcam in other skills

if you want to get a file path for the latest picture you can use the
messagebus to get a file path


    def initialize(self):
        self.add_event("webcam.picture", self.get_the_feed)
        self.bus.emit(Message("webcam.request"))


    def get_the_feed(self, message):
        file_path = message.data.get("path")



