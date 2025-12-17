from viam.proto.app.robot import ComponentConfig, ServiceConfig
from viam.utils import dict_to_struct
from typing import List, Dict

from unittest.mock import patch

from src.blurry_classifier_module import BlurryClassifier
from tests.fake_camera import FakeCamera

import pytest


CAMERA_NAME = "fake_cam"

config = ServiceConfig(
    attributes=dict_to_struct(
        {
            "camera_name": CAMERA_NAME,
        }
    ))

def get_vision_service(blurry: bool = True) -> BlurryClassifier:
    service = BlurryClassifier("test")
    cam = FakeCamera(CAMERA_NAME, blurry)
    camera_name = cam.get_resource_name(CAMERA_NAME)
    service.validate_config(config)
    service.reconfigure(config, dependencies={camera_name: cam})
    return service

class TestBlurryClassifier:
    def test_empty(self):
        blurry_classifier = BlurryClassifier("test_blurry_classifier")
        with pytest.raises(ValueError, match="A camera name is required for face_identification vision service module."):
            blurry_classifier.validate_config(ServiceConfig(attributes=dict_to_struct({})))

    @pytest.mark.asyncio
    @patch('viam.components.camera.Camera.get_resource_name', return_value=CAMERA_NAME)
    async def test_reconfigure(self, fake_cam):
        blurry_classifier = get_vision_service()

        assert blurry_classifier.camera_name == CAMERA_NAME
        assert blurry_classifier.camera is not None

    @pytest.mark.asyncio
    @patch('viam.components.camera.Camera.get_resource_name', return_value=CAMERA_NAME)
    async def test_get_classifications(self, fake_cam):
        blurry_classifier = get_vision_service(True)

        # Test with a blurry image
        images, _ = await blurry_classifier.camera.get_images()
        image = images[0]
        print(image)
        result = await blurry_classifier.get_classifications(
            image = images[0],
            count=1,
        )

        assert result[0].class_name == "blurry"
        assert result[0].confidence == 1.0

        blurry_classifier = get_vision_service(False)
        # Test with a non-blurry image
        images, _ =await blurry_classifier.camera.get_images()
        result = await blurry_classifier.get_classifications(
            image= images[0],
            count=1,
        )

        assert result == []

    @pytest.mark.asyncio
    @patch('viam.components.camera.Camera.get_resource_name', return_value=CAMERA_NAME)
    async def test_capture_all_from_camera(self, fake_cam):
        blurry_classifier = get_vision_service(True)

        # Test with a blurry image
        result = await blurry_classifier.capture_all_from_camera(
            camera_name=CAMERA_NAME,
            return_image=True,
            return_classifications=True,
        )

        assert result.image is not None
        assert result.classifications[0].class_name == "blurry"
        assert result.classifications[0].confidence == 1.0

    @pytest.mark.asyncio
    @patch('viam.components.camera.Camera.get_resource_name', return_value=CAMERA_NAME)
    async def test_with_default_camera(self, fake_cam):
        blurry_classifier = get_vision_service(True)

        # Test with empty camera name
        result = await blurry_classifier.capture_all_from_camera(
            camera_name="",
            return_image=True,
            return_classifications=True,
        )

        assert result.image is not None
        assert result.classifications[0].class_name == "blurry"
        assert result.classifications[0].confidence == 1.0

        result = await blurry_classifier.get_classifications_from_camera(
            camera_name="",
            count=1,
        )

        assert result[0].class_name == "blurry"
        assert result[0].confidence == 1.0

        # Test with wrong camera name
        with pytest.raises(ValueError, match="Camera name wrong_camera does not match the camera name fake_cam in the config."):
            await blurry_classifier.capture_all_from_camera(
                camera_name="wrong_camera",
                return_image=True,
                return_classifications=True,
            )

        with pytest.raises(ValueError, match="Camera name wrong_camera does not match the camera name fake_cam in the config."):
            await blurry_classifier.get_classifications_from_camera(
                camera_name="wrong_camera",
                count=1,
            )


