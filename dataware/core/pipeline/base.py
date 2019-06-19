


def manage_processors(method):
    "Enter and exit all processors that have with functionality"
    def wrapped(*args, **kwargs):
        
        with contextlib.ExitStack() as stack:
            # using with statement in all of the loaders
            self = args[0]
            args = args[1:]

            for proc in self.processors:
                if hasattr(proc, '__enter__'):
                    stack.enter_context(loader)
                
            return method(self, *args, **kwargs)
        
    return wrapped


class PipelineBase:

    def __init__(self):
        pass

    @manage_processors
    def execute(self):
        self._run_processors()

    def _run_processors(self, input_data=None, processors=None):
        "Run all processors or defined processors"
        if processors is None:
            processors = self.processors

        for processor in processors:
            input_data = self._run_processor(processor, input_data=input_data)

        return input_data

    def _run_processor(processor, input_data=None):

        if isinstance(processor, ExtractorBase):
            input_data = processor.extract()

        elif isinstance(processor, LoaderBase):
            if self.is_batch:
                processor.stage(input_data)
            else:
                processor.load(input_data)

        elif isinstance(processor, TransformerBase):
            input_data = processor.transform(input_data)

        else:
            processor.process(input_data)

        return output_data