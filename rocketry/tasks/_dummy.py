from rocketry.core import Task
class _DummyTask(Task):
    """
    Not used within core application. Only used in UnitTests
    DummyTask which inherits task and performs forward_refs
    to allow for use inside unit tests. Provides basic implementation
    of Task classs and overwrites required abstractmethods.
    """
    def execute(self, *args, **kwargs):
        return
