
from dataclasses import dataclass
from core.ports import IOCR, IRepository

@dataclass
class SavePageService:
    repo: IRepository
    ocr: IOCR

    def save_drawn_page(self, image_path: str, ts_iso: str) -> tuple[int,int]:
        page_id = self.repo.add_page(image_path, ts_iso)
        # Lite: без OCR/AI
        return page_id, 0
