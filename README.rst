The datahub is a platform for people to share data and to cooperate on 
data refinement and management. 

Installation
============

To install datahub, you need to load its dependencies. For that, you 
may want to create a virtualenv before you perform these steps::
  
  pip install -r pip-requirements.txt
  python setup.py develop

If you also want to run asynchronous tasks, you will need to create 
a file called `celeryconfig.py`, normally by symlinking either to your
local configuration or to `datahub/default_settings.py`. 


