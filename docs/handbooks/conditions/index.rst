.. _condition-handbook:

Conditions
==========

Rocketry's scheduling system works with conditions
that are either true or false. A simple condition
could be *time is now between 8 am and 2 pm* (12-hour clock) 
or *time is now between 08:00 and 14:00* (24-hour clock).
If current time is inside this range, the condition
is true and if not, then it's false. If this is a condition 
for a task, it runs if the the current time is in the range. 

The conditions can be combinded using logical operations:
**AND**, **OR**, **NOT**. They also can be nested using 
parentheses.

There are three ways of creating conditions in Rocketry:

- Condition syntax
- Condition API
- Condition classes

All of the above produce instances of conditions that 
can be used as the starting conditions of tasks or the 
shut down condition of a scheduler. The condition syntax 
turns the condition strings to the condition API's 
components and condition API's components are turned to
instances of the actual conditions.


.. toctree::
   :maxdepth: 3
   :caption: Contents:

   api/index
   syntax/index
   classes
   comparisons