from .pipe import PipeMode


class ClipHistMode(PipeMode):
    def get_main_item_label(self, item: str):
        try:
            i, text = item.split('\t', maxsplit=1)
        except ValueError:
            return ''
        else:
            return text
