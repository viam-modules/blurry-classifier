from viam.proto.app.robot import ComponentConfig, ServiceConfig
from viam.utils import dict_to_struct
from typing import List, Dict

from unittest.mock import patch

from src.blurry_classifier_module import BlurryClassifier
from tests.fake_camera import FakeCamera

import pytest


CAMERA_NAME = "fake_cam"
BLURRINESS_THRESHOLD = 300.0
config = ServiceConfig(
    attributes=dict_to_struct(
        {
            "camera_name": CAMERA_NAME,
            "blurry_threshold": BLURRINESS_THRESHOLD,
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
        assert blurry_classifier.blurry_threshold == BLURRINESS_THRESHOLD
        assert blurry_classifier.camera is not None

    @pytest.mark.asyncio
    @patch('viam.components.camera.Camera.get_resource_name', return_value=CAMERA_NAME)
    async def test_get_classifications(self, fake_cam):
        blurry_classifier = get_vision_service(True)

        # Test with a blurry image
        result = await blurry_classifier.get_classifications(
            image= await blurry_classifier.camera.get_image(),
            count=1,
        )

        assert result[0].class_name == "blurry"
        assert result[0].confidence == 1.0

        blurry_classifier = get_vision_service(False)
        # Test with a non-blurry image
        result = await blurry_classifier.get_classifications(
            image=await blurry_classifier.camera.get_image(),
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
