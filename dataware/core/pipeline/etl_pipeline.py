
from .base import manage_processors

class ETLPipeline:

    def __init__(self, *processors):
        self.processors = processors

    @manage_processors
    def execute(self):
        if self.is_batch:

            for input_data in self.extractor:
                self._run_processors(input_data)
            

    def _run_postprocs(self, data):
        for proc in self.middlewares:
            if isinstance(proc, TransformerBase):
                return proc.process(data)
