# blurry-classifier 

This module implements a Vision service that performs image blurriness classification. It uses the Laplacian variance method to determine the blurriness of an image from a camera.

## Getting started

Start by [configuring a camera](https://docs.viam.com/components/camera/webcam/) on your robot. Remember the name you give to the camera, it will be important later.

> [!NOTE]
> Before configuring your camera or vision service, you must [create a robot](https://docs.viam.com/manage/fleet/robots/#add-a-new-robot).

> [!NOTE]
> If you run this on a non-Debian-based flavor of Linux, you need to ensure that libGL.so.1 is installed on your system! It's probably already installed, unless you're using a headless setup. Ubuntu is Debian-based, so this note doesn't apply on Ubuntu.

## Configuration

Navigate to the **Config** tab of your robot’s page in [the Viam app](https://app.viam.com/). Click on the **Services** subtab and click **Create service**. Select the `vision` type, then select the `blurry-classifier` model. Enter a name for your service and click **Create**.

On the new component panel, copy and paste the following attribute template into your base’s **Attributes** box.
```json
{
"camera_name": "myCam",
"blurry_threshold": 100.0
}
```

#### Attributes

The following attributes are available for this model:

| Name          | Type   | Inclusion | Description                |
|---------------|--------|-----------|----------------------------|
| `camera_name` | string  | Required  | The name of the camera configured on your robot. |
| `blurry_threshold` | float | Optional  | The threshold _below_ which an image would be considered blurry. High laplacian variance corresponds to low blurriness. |

#### Example Configuration

```json
{
  "modules": [
    {
      "type": "registry",
      "name": "viam-blurry-classifier",
      "module_id": "viam:blurry-classifier",
      "version": "0.0.1"
    }
  ],
  "services": [
    {
      "name": "myBlurryClassifier",
      "type": "vision",
      "namespace": "rdk",
      "model": "viam:blurry-classifier:blurry-classifier",
      "attributes": {
        "camera_name": "myCam",
        "blurry_threshold": 100.0
      }
    }
  ]
}
```

### Usage

This module is made for use with the following methods of the [vision service API](https://docs.viam.com/services/vision/#api):
- [`GetClassifications()`](https://docs.viam.com/dev/reference/apis/services/vision/#getclassifications)
- [`GetClassificationsFromCamera()`](https://docs.viam.com/dev/reference/apis/services/vision/#getclassificationsfromcamera)
- [`CaptureAllFromCamera()`](https://docs.viam.com/dev/reference/apis/services/vision/#captureallfromcamera)

When the module returns classifications, the `class_name` will always be "blurry", and the `confidence` will always be 1.0. If the laplacian variance is below the threshold defined in the config, then no classifications will be returned. 
