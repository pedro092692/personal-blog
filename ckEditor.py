from flask_ckeditor import CKEditor


class Editor:

    def __init__(self, app):
        ckeditor = CKEditor(app)
