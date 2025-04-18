import os
from typing import Any, Coroutine, List, Tuple, Union

from PIL import Image
from viam.components.camera import Camera
from viam.gen.component.camera.v1.camera_pb2 import GetPropertiesResponse
from viam.media.utils import pil
from viam.media.video import CameraMimeType, NamedImage, ViamImage
from viam.proto.common import ResponseMetadata


def read_image(name: str):
    return Image.open(os.path.join("./tests", "img", name + ".jpg"))


class FakeCamera(Camera):
    def __init__(self, name: str):
        super().__init__(name=name)
        self.images = [read_image("blurry"), read_image("not_blurry")]

    async def get_image(self, mime_type: str = "", blurry: bool = True) -> Coroutine[Any, Any, ViamImage]:
        return pil.pil_to_viam_image(self.images[0 if blurry else 1], CameraMimeType.JPEG)

    async def get_images(
        self,
    ) -> Coroutine[Any, Any, Tuple[Union[List[NamedImage], ResponseMetadata]]]:
        raise NotImplementedError

    async def get_properties(self) -> Coroutine[Any, Any, GetPropertiesResponse]:
        raise NotImplementedError

    async def get_point_cloud(self) -> Coroutine[Any, Any, Tuple[Union[bytes, str]]]:
        raise NotImplementedError
