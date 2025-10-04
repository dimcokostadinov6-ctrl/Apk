
from infra.database_sqlite import SQLiteRepo
from infra.ocr_stub import NoOCR
from core.services import SavePageService
from ui_kivy.app import VeresiyaApp

repo = SQLiteRepo(); ocr = NoOCR(); service = SavePageService(repo=repo, ocr=ocr)
if __name__ == '__main__':
    VeresiyaApp(repo=repo, service=service).run()
