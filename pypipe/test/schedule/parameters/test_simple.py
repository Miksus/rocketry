
from pypipe import Scheduler, MultiScheduler, FuncTask
from pypipe.task.base import Task, clear_tasks
from pypipe.conditions import scheduler_cycles
from pypipe import reset
from pypipe.parameters import Parameters, ParameterSet

import pytest
import logging
import sys


def do_stuff_kwargs(*, x, y):
    assert x == 'keyword x'
    assert y == 'keyword y'

def do_stuff_args(arg1, arg2):
    assert arg1 == 'positional 1'
    assert arg2 == 'positional 2'

def do_stuff_args_kwargs(arg1, arg2, *, x, y):
    assert arg1 == 'positional 1'
    assert arg2 == 'positional 2'
    assert x == 'keyword x'
    assert y == 'keyword y'

def test_single_kwargs(tmpdir):
    reset()
    with tmpdir.as_cwd() as old_dir:


        task_kwarg = FuncTask(do_stuff_kwargs)
        #task_arg = FuncTask(failing)
        scheduler = Scheduler(
            [
                task_kwarg,
            ], 
            shut_condition=scheduler_cycles >= 3,
            parameters=Parameters(ParameterSet(x='keyword x', y='keyword y'))
        )
        
        scheduler()
        assert scheduler.n_cycles == 3

        history = task_kwarg.get_history()
        assert 3 == (history["action"] == "run").sum()
        assert 3 == (history["action"] == "success").sum()


def test_single_args(tmpdir):
    reset()
    with tmpdir.as_cwd() as old_dir:


        task_args = FuncTask(do_stuff_args)
        #task_arg = FuncTask(failing)
        scheduler = Scheduler(
            [
                task_args,
            ], 
            shut_condition=scheduler_cycles >= 3,
            parameters=Parameters(ParameterSet('positional 1', 'positional 2'))
        )
        
        scheduler()
        assert scheduler.n_cycles == 3

        history = task_args.get_history()
        assert 3 == (history["action"] == "run").sum()
        assert 3 == (history["action"] == "success").sum()


def test_single_args_kwargs(tmpdir):
    reset()
    with tmpdir.as_cwd() as old_dir:


        task_args_kwargs = FuncTask(do_stuff_args_kwargs)
        #task_arg = FuncTask(failing)
        params = Parameters(
            ParameterSet('positional 1', 'positional 2', x='keyword x', y='keyword y')
        )
        scheduler = Scheduler(
            [
                task_args_kwargs,
            ], 
            shut_condition=scheduler_cycles >= 3,
            parameters=params
        )
        
        scheduler()
        assert scheduler.n_cycles == 3

        history = task_args_kwargs.get_history()
        assert 3 == (history["action"] == "run").sum()
        assert 3 == (history["action"] == "success").sum()


def test_multi(tmpdir):
    reset()
    with tmpdir.as_cwd() as old_dir:

        task_args = FuncTask(do_stuff_args)
        task_kwargs = FuncTask(do_stuff_kwargs)
        task_args_kwargs = FuncTask(do_stuff_args_kwargs)
        #task_arg = FuncTask(failing)
        params = Parameters(
            ParameterSet('positional 1', 'positional 2', x='keyword x', y='keyword y')
        )
        scheduler = Scheduler(
            [
                task_args, task_kwargs, task_args_kwargs
            ], 
            shut_condition=scheduler_cycles >= 3,
            parameters=params
        )
        
        scheduler()
        assert scheduler.n_cycles == 3

        for task in (task_args, task_kwargs, task_args_kwargs):
            history = task.get_history()
            assert 3 == (history["action"] == "run").sum()
            assert 3 == (history["action"] == "success").sum()


# Multiprocess
def test_single_kwargs_multiprocess(tmpdir):
    reset()
    with tmpdir.as_cwd() as old_dir:


        task_kwarg = FuncTask(do_stuff_kwargs)
        #task_arg = FuncTask(failing)
        scheduler = Scheduler(
            [
                task_kwarg,
            ], 
            shut_condition=scheduler_cycles >= 3,
            parameters=Parameters(ParameterSet(x='keyword x', y='keyword y'))
        )
        
        scheduler()
        assert scheduler.n_cycles == 3

        history = task_kwarg.get_history()
        assert 3 == (history["action"] == "run").sum()
        assert 3 == (history["action"] == "success").sum()


def test_single_args_multiprocess(tmpdir):
    reset()
    with tmpdir.as_cwd() as old_dir:


        task_args = FuncTask(do_stuff_args)
        #task_arg = FuncTask(failing)
        scheduler = Scheduler(
            [
                task_args,
            ], 
            shut_condition=scheduler_cycles >= 3,
            parameters=Parameters(ParameterSet('positional 1', 'positional 2'))
        )
        
        scheduler()
        assert scheduler.n_cycles == 3

        history = task_args.get_history()
        assert 3 == (history["action"] == "run").sum()
        assert 3 == (history["action"] == "success").sum()


def test_single_args_kwargs_multiprocess(tmpdir):
    reset()
    with tmpdir.as_cwd() as old_dir:


        task_args_kwargs = FuncTask(do_stuff_args_kwargs)
        #task_arg = FuncTask(failing)
        params = Parameters(
            ParameterSet('positional 1', 'positional 2', x='keyword x', y='keyword y')
        )
        scheduler = Scheduler(
            [
                task_args_kwargs,
            ], 
            shut_condition=scheduler_cycles >= 3,
            parameters=params
        )
        
        scheduler()
        assert scheduler.n_cycles == 3

        history = task_args_kwargs.get_history()
        assert 3 == (history["action"] == "run").sum()
        assert 3 == (history["action"] == "success").sum()


def test_multi_multiprocess(tmpdir):
    reset()
    with tmpdir.as_cwd() as old_dir:

        task_args = FuncTask(do_stuff_args)
        task_kwargs = FuncTask(do_stuff_kwargs)
        task_args_kwargs = FuncTask(do_stuff_args_kwargs)
        #task_arg = FuncTask(failing)
        params = Parameters(
            ParameterSet('positional 1', 'positional 2', x='keyword x', y='keyword y')
        )
        scheduler = Scheduler(
            [
                task_args, task_kwargs, task_args_kwargs
            ], 
            shut_condition=scheduler_cycles >= 3,
            parameters=params
        )
        
        scheduler()
        assert scheduler.n_cycles == 3

        for task in (task_args, task_kwargs, task_args_kwargs):
            history = task.get_history()
            assert 3 == (history["action"] == "run").sum()
            assert 3 == (history["action"] == "success").sum()


