# Camera Skill

Camera skill for OpenVoiceOS

## Description

This skill allows you to take pictures using a connected webcam. You can configure various settings to customize its behavior.

## Examples

* "Take a picture"

## Settings

The `settings.json` file allows you to configure the behavior of the Camera Skill. Below are the available settings:

| Setting Name         | Type     | Default       | Description                                                                 |
|----------------------|----------|---------------|-----------------------------------------------------------------------------|
| `video_source`       | Integer  | `0`           | Specifies the camera to use. `0` is the default system webcam.             |
| `play_sound`         | Boolean  | `true`        | Whether to play a sound when a picture is taken.                           |
| `camera_sound_path`  | String   | `camera.wav`  | Path to the sound file to play when taking a picture.                      |
| `pictures_folder`    | String   | `~/Pictures`  | Directory where pictures are saved.                                        |
| `keep_camera_open`   | Boolean  | `false`       | Whether to keep the camera stream open after taking a picture.             |

### Example `settings.json`

```json
{
  "video_source": 0,
  "play_sound": true,
  "camera_sound_path": "/path/to/camera.wav",
  "pictures_folder": "/home/user/Pictures",
  "keep_camera_open": false
}
```
