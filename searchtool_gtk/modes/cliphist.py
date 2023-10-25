from .pipe import PipeMode


# This is an abstract base class for several real modes
class ClipHistMode(PipeMode):
    def get_main_item_label(self, item: str):
        i, text = item.split('\t', maxsplit=1)
        return text
