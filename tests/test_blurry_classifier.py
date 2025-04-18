from viam.proto.app.robot import ComponentConfig, ServiceConfig
from viam.utils import dict_to_struct
from typing import List, Dict

from unittest.mock import patch

from src.blurry_classifier_module import BlurryDetector
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

def get_vision_service():
    service = BlurryDetector("test")
    cam = FakeCamera(CAMERA_NAME)
    camera_name = cam.get_resource_name(CAMERA_NAME)
    cfg = config
    service.validate_config(cfg)
    service.reconfigure(cfg, dependencies={camera_name: cam})
    return service

class TestBlurryDetector:
    def test_empty(self):
        blurry_detector = BlurryDetector("test_blurry_detector")
        with pytest.raises(ValueError, match="A camera name is required for face_identification vision service module."):
            blurry_detector.validate_config(ServiceConfig(attributes=dict_to_struct({})))

    @pytest.mark.asyncio
    @patch('viam.components.camera.Camera.get_resource_name', return_value="fake_cam")
    async def test_reconfigure(self, fake_cam):
        blurry_detector = get_vision_service()

        assert blurry_detector.camera_name == CAMERA_NAME
        assert blurry_detector.blurry_threshold == BLURRINESS_THRESHOLD
        assert blurry_detector.camera is not None

    @pytest.mark.asyncio
    @patch('viam.components.camera.Camera.get_resource_name', return_value="fake_cam")
    async def test_get_classifications(self, fake_cam):
        blurry_detector = get_vision_service()

        # Test with a blurry image
        result = await blurry_detector.get_classifications(
            image= await blurry_detector.camera.get_image(True),
            count=1,
        )

        assert result[0].class_name == "blurry"
        assert result[0].confidence == 0.5

        # Test with a non-blurry image
        result = await blurry_detector.get_classifications(
            image=await blurry_detector.camera.get_image(blurry=False),
            count=1,
        )

        assert result == []

    @pytest.mark.asyncio
    @patch('viam.components.camera.Camera.get_resource_name', return_value="fake_cam")
    async def test_capture_all_from_camera(self, fake_cam):
        blurry_detector = get_vision_service()

        # Test with a blurry image
        result = await blurry_detector.capture_all_from_camera(
            camera_name=CAMERA_NAME,
            return_image=True,
            return_classifications=True,
        )

        assert result.image is not None
        assert result.classifications[0].class_name == "blurry"
        assert result.classifications[0].confidence == 0.5
