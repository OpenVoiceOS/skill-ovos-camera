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


### Additional Steps for Raspberry Pi Users

If you plan to use this skill on a Raspberry Pi, it requires access to the `libcamera` package for the Picamera2 library to function correctly. Due to how `libcamera` is installed on the Raspberry Pi (system-wide), additional steps are necessary to ensure compatibility when using a Python virtual environment (venv).

In these examples we use the default .venv location from ovos-installer, `~/.venvs/ovos`, adjust as needed

#### **Steps to Enable `libcamera` in Your Virtual Environment**

1. **Install Required System Packages**  
   Before proceeding, ensure that `libcamera` and its dependencies are installed on your Raspberry Pi. Run the following commands:  
   ```bash
   sudo apt install -y python3-libcamera python3-kms++ libcap-dev
   ```

2. **Modify the Virtual Environment Configuration**  
   If you already have a virtual environment set up, enable access to system-wide packages by modifying the `pyvenv.cfg` file in the virtual environment directory:  
   ```bash
   nano ~/.venvs/ovos/pyvenv.cfg
   ```

   Add or update the following line:  
   ```plaintext
   include-system-site-packages = true
   ```

   Save the file and exit.

3. **Verify Access to `libcamera`**  
   Activate your virtual environment:  
   ```bash
   source ~/.venvs/ovos/bin/activate
   ```

   Check if the `libcamera` package is accessible:  
   ```bash
   python3 -c "import libcamera; print('libcamera is accessible')"
   ```

#### **Why Are These Steps Necessary?**
The `libcamera` package is not available on PyPI and is installed system-wide on the Raspberry Pi. Virtual environments typically isolate themselves from system-wide Python packages, so these adjustments allow the skill to access `libcamera` while still benefiting from the isolation provided by a venv.

#### **Notes**
- These steps are specific to Raspberry Pi users who want to utilize the Picamera2 library for camera functionality. On other platforms, the skill defaults to using OpenCV, which does not require additional configuration.
- Ensure that `libcamera` is installed on your Raspberry Pi before attempting these steps. You can test this by running:  
  ```bash
  libcamera-still --version
  ```