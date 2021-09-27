from redengine.core import Task, Scheduler

from redengine.tasks import FuncTask
from redengine.conditions import SchedulerCycles, true

def test_task_init():
    timeline = []

    @Task.hook_init
    def myhook(task):
        timeline.append("Function hook called")
        assert isinstance(task, DummyTask)
        assert not hasattr(task, "name") # Should not yet have created this attr
        task.myattr = "x"
    
    @Task.hook_init
    def mygenerhook(task):
        timeline.append("Generator hook called (pre)")
        assert isinstance(task, DummyTask)
        assert not hasattr(task, "name") # Should not yet have created this attr
        yield 
        assert hasattr(task, "session") # Should now have it
        timeline.append("Generator hook called (post)")

    class DummyTask(Task):
        __register__ = False

        def execute(self, *args, **kwargs):
            return 


    assert Task.init_hooks == [myhook, mygenerhook] # The func is in different namespace thus different

    timeline.append("Main")
    mytask = DummyTask(name="dummy")
    assert timeline == [
        "Main",
        "Function hook called",
        "Generator hook called (pre)",
        "Generator hook called (post)",
    ]
    assert mytask.myattr == "x"


def test_scheduler_startup(session):
    timeline = []

    @Scheduler.hook_startup
    def my_startup_hook(sched):
        assert isinstance(sched, Scheduler)
        timeline.append("ran hook (startup)")

    @Scheduler.hook_cycle
    def my_cycle_hook(sched):
        assert isinstance(sched, Scheduler)
        timeline.append("ran hook (cycle)")

    @Scheduler.hook_shutdown
    def my_shutdown_hook(sched):
        assert isinstance(sched, Scheduler)
        timeline.append("ran hook (shutdown)")


    @Scheduler.hook_startup
    def my_startup_hook_generator(sched):
        assert isinstance(sched, Scheduler)
        timeline.append("ran hook (startup, generator first)")
        yield
        timeline.append("ran hook (startup, generator second)")

    @Scheduler.hook_cycle
    def my_cycle_hook_generator(sched):
        assert isinstance(sched, Scheduler)
        timeline.append("ran hook (cycle, generator first)")
        yield
        timeline.append("ran hook (cycle, generator second)")

    @Scheduler.hook_shutdown
    def my_shutdown_hook_generator(sched):
        assert isinstance(sched, Scheduler)
        timeline.append("ran hook (shutdown, generator first)")
        yield
        timeline.append("ran hook (shutdown, generator second)")
    

    FuncTask(lambda: timeline.append("ran TASK (startup)"), name="start", on_startup=True, execution="main")
    FuncTask(lambda: timeline.append("ran TASK (normal 1)"), name="1", execution="main", start_cond=true)
    FuncTask(lambda: timeline.append("ran TASK (normal 2)"), name="2", execution="main", start_cond=true)
    FuncTask(lambda: timeline.append("ran TASK (shutdown)"), name="shut", on_shutdown=True, execution="main")

    session.scheduler.shut_cond = SchedulerCycles(_eq_=2)
    session.start()
    
    assert timeline == [
        "ran hook (startup)", 
        "ran hook (startup, generator first)", 
        "ran TASK (startup)", 
        "ran hook (startup, generator second)", 

        "ran hook (cycle)", 
        "ran hook (cycle, generator first)", 
        "ran TASK (normal 1)",
        "ran TASK (normal 2)",
        "ran hook (cycle, generator second)", 

        "ran hook (cycle)", 
        "ran hook (cycle, generator first)", 
        "ran TASK (normal 1)",
        "ran TASK (normal 2)",
        "ran hook (cycle, generator second)", 

        "ran hook (shutdown)", 
        "ran hook (shutdown, generator first)", 
        "ran TASK (shutdown)", 
        "ran hook (shutdown, generator second)", 
    ]