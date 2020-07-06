
def test_from_yaml(tmpdir):
    p = tmpdir.join("schedconf.yaml") # .mkdir("sub")
    p.write("""
maintain_tasks: maintain/tasks
shut_condition: scheduler_on.past("5 hours") 
logger: csv
tasks:
    analysis:
        

    """)