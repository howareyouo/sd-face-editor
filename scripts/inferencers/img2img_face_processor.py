from typing import Union

from modules.processing import StableDiffusionProcessingImg2Img, process_images
from PIL import Image

from scripts.entities.face import Face
from scripts.use_cases.face_processor import FaceProcessor


class Img2ImgFaceProcessor(FaceProcessor):
    def name(self) -> str:
        return "img2img"

    def process(
        self,
        face: Face,
        p: StableDiffusionProcessingImg2Img,
        strength1: Union[float, int],
        pp: str = "",
        np: str = "",
        **kwargs,
    ) -> Image:
        p.init_images = [face.image]
        p.width = face.image.width
        p.height = face.image.height
        p.denoising_strength = strength1
        p.do_not_save_samples = True

        if len(pp) > 0:
            p.prompt = pp
        if len(np) > 0:
            p.negative_prompt = np

        # print(f"[Face Editor] Prompt for {face.face_area.tag}: {p.prompt}")

        proc = process_images(p)
        return proc.images[0]
