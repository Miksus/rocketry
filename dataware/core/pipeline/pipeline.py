

from .base import manage_processors

class Pipeline:

    def __init__(self, *processors):
        self.processors = processors

    @manage_processors
    def execute(self):
       
        if self.is_batch:
             post_processors = self.processors[1:]
            for input_data in self.processors[0]:
                self._run_processors(
                    input_data, 
                    processors=post_processors
                )
        else:
            self._run_processors(
                processors=self.processors
            )


    @property
    def loaders(self):
        return [proc for proc in self.processors if isinstance(proc, LoaderBase)]


    