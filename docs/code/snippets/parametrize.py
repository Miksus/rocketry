from rocketry.args import Arg, CliArg, EnvArg, FuncArg


def get_value():
    return 'Hello World'

@app.param('my_param')
def get_session_param():
    "Session level parameter (named as 'my_param')"
    return 'Hello Python'

@app.task()
def do_with_param(arg1=Arg('my_param'), arg2=FuncArg(get_value),
                  arg3=EnvArg('ENV_VARIABLE'), arg4=CliArg('--cli_arg')):
    ...
