import asyncio
from typing import ClassVar, List, Mapping, Optional, Sequence
from typing_extensions import Self

from viam.components.camera import Camera
from viam.media.video import CameraMimeType, ViamImage
from viam.module.module import Module
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import PointCloudObject, ResourceName
from viam.proto.service.vision import Classification, Detection
from viam.resource.base import ResourceBase
from viam.resource.easy_resource import EasyResource
from viam.resource.types import Model, ModelFamily
from viam.services.vision import *
from viam.utils import ValueTypes

import cv2 as cv

from src.utils import decode_image


class BlurryDetector(Vision, EasyResource):
    MODEL: ClassVar[Model] = Model(
        ModelFamily("viam", "blurry-detector"), "blurry-detector"
    )

    def __init__(self, name: str):
        super().__init__(name=name)
        self.camera = None
        self.camera_name = None
        self.blurry_threshold = 1000.0

    @classmethod
    def new(
        cls,
        config: ComponentConfig,
        dependencies: Mapping[ResourceName, ResourceBase],
    ) -> Self:
        """
        This method creates a new instance of this Vision service.  The default
        implementation sets the name from the `config` parameter and then calls
        `reconfigure`.

        Args:
            config (ComponentConfig): The configuration for this resource
            dependencies (Mapping[ResourceName, ResourceBase]): The
                dependencies (both implicit and explicit)

        Returns:
            Self: The resource
        """
        service = cls(config.name)
        service.reconfigure(config, dependencies)
        return service

    @classmethod
    def validate_config(cls, config: ComponentConfig) -> Sequence[str]:
        """
        This method allows you to validate the configuration object received
        from the machine, as well as to return any implicit dependencies based
        on that `config`.

        Args:
            config (ComponentConfig): The configuration for this resource

        Returns:
            Sequence[str]: A list of implicit dependencies
        """
        camera_name = config.attributes.fields["camera_name"].string_value
        if camera_name == "":
            raise ValueError(
                "A camera name is required for face_identification vision service module."
            )
        return [camera_name]

    def reconfigure(
        self,
        config: ComponentConfig,
        dependencies: Mapping[ResourceName, ResourceBase],
    ) -> None:
        """
        This method allows you to dynamically update your service when it
        receives a new `config` object.

        Args:
            config (ComponentConfig): The new configuration
            dependencies (Mapping[ResourceName, ResourceBase]): Any
                dependencies (both implicit and explicit)
        """
        self.camera_name = config.attributes.fields["camera_name"].string_value
        self.camera = dependencies[Camera.get_resource_name(self.camera_name)]
        if "blurry_threshold" in config.attributes.fields:
            self.blurry_threshold = config.attributes.fields["blurry_threshold"].number_value

    async def capture_all_from_camera(
        self,
        camera_name: str,
        return_image: bool = False,
        return_classifications: bool = False,
        return_detections: bool = False,
        return_object_point_clouds: bool = False,
        *,
        extra: Optional[Mapping[str, ValueTypes]] = None,
        timeout: Optional[float] = None,
    ) -> CaptureAllResult:
        if camera_name not in (self.camera_name, ""):
            raise ValueError(
                f"Camera name {camera_name} does not match the camera name {self.camera_name} in the config."
            )
        im = await self.camera.get_image(mime_type=CameraMimeType.JPEG)
        classifications = None
        if return_classifications:
            classifications = await self.get_classifications(
                im, 1, extra=extra, timeout=timeout
            )

        return CaptureAllResult(image=im, classifications=classifications)

    async def get_detections_from_camera(
        self,
        camera_name: str,
        *,
        extra: Optional[Mapping[str, ValueTypes]] = None,
        timeout: Optional[float] = None,
    ) -> List[Detection]:
        raise NotImplementedError()

    async def get_detections(
        self,
        image: ViamImage,
        *,
        extra: Optional[Mapping[str, ValueTypes]] = None,
        timeout: Optional[float] = None,
    ) -> List[Detection]:
        raise NotImplementedError()

    async def get_classifications_from_camera(
        self,
        camera_name: str,
        count: int,
        *,
        extra: Optional[Mapping[str, ValueTypes]] = None,
        timeout: Optional[float] = None,
    ) -> List[Classification]:
        if camera_name not in (self.camera_name, ""):
            raise ValueError(
                f"Camera name {camera_name} does not match the camera name {self.camera_name} in the config."
            )
        im = await self.camera.get_image(mime_type=CameraMimeType.JPEG)
        return self.get_classifications(im, 1, extra=extra, timeout=timeout)

    async def get_classifications(
        self,
        image: ViamImage,
        count: int,
        *,
        extra: Optional[Mapping[str, ValueTypes]] = None,
        timeout: Optional[float] = None,
    ) -> List[Classification]:
        img = decode_image(image)
        blurriness = cv.Laplacian(img, cv.CV_64F).var()
        if blurriness < self.blurry_threshold:
            return [Classification(class_name="blurry", confidence=0.5)]

        return []


    async def get_object_point_clouds(
        self,
        camera_name: str,
        *,
        extra: Optional[Mapping[str, ValueTypes]] = None,
        timeout: Optional[float] = None,
    ) -> List[PointCloudObject]:
        raise NotImplementedError()

    async def get_properties(
        self,
        *,
        extra: Optional[Mapping[str, ValueTypes]] = None,
        timeout: Optional[float] = None,
    ) -> Vision.Properties:
        return Vision.Properties(
            classifications_supported=True,
            detections_supported=False,
            object_point_clouds_supported=False,
        )


if __name__ == "__main__":
    asyncio.run(Module.run_from_registry())
