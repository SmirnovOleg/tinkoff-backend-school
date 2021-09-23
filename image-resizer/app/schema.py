from pydantic import BaseModel, validator

from app.utils import ImageEncoder


class ImageRequestBodyModel(BaseModel):
    img_data: str

    @validator('img_data')
    def must_be_base64_image(cls, value: str) -> str:
        try:
            ImageEncoder.decode_image(value)
        except Exception as e:
            raise ValueError('must be a valid base64-decoded image') from e
        else:
            return value

    @validator('img_data')
    def must_be_png(cls, value: str) -> str:
        image = ImageEncoder.decode_image(value)
        if image.format != 'PNG':
            raise ValueError('must be a PNG image')
        return value

    @validator('img_data')
    def must_be_square(cls, value: str) -> str:
        image = ImageEncoder.decode_image(value)
        width, height = image.size
        if width != height:
            raise ValueError('must be a square image')
        return value
