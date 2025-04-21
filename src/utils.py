"""Utility file including methods for image decoding"""

from typing import Union
from io import BytesIO
from PIL import Image
from viam.logging import getLogger
from viam.media.video import CameraMimeType
from viam.media.video import ViamImage
import numpy as np

LOGGER = getLogger(__name__)

SUPPORTED_IMAGE_TYPE = [
    CameraMimeType.JPEG,
    CameraMimeType.PNG,
    CameraMimeType.VIAM_RGBA,
]
LIBRARY_SUPPORTED_FORMATS = ["JPEG", "PNG", "VIAM_RGBA"]

def decode_image(image: Union[Image.Image, ViamImage, np.ndarray]) -> np.ndarray:
    """decode image to BGR numpy array
    Args:
        raw_image (Union[Image.Image, RawImage])
    Returns:
        np.ndarray: BGR numpy array
    """
    if isinstance(image, ViamImage):
        if image.mime_type not in SUPPORTED_IMAGE_TYPE:
            LOGGER.error(
                "Unsupported image type: %s. Supported types are %s.",
                image.mime_type,
                SUPPORTED_IMAGE_TYPE,
            )

            raise ValueError(f"Unsupported image type: {image.mime_type}.")

        pil_image = Image.open(BytesIO(image.data), formats=LIBRARY_SUPPORTED_FORMATS).convert(
            "RGB"
        )
    else:
        pil_image = image
        
    res = pil_image.convert("RGB")
    rgb = np.array(res)
    return rgb
