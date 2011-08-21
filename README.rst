The datahub is a platform for people to share data and to cooperate on 
data refinement and management. The site allows users to share simple
``resources`` (e.g. a file or an API endpoint address) and to bundle 
those into ``datasets``: groupings for multiple represenatations of a 
single logic dataset, lists of resources on a shared topic or a list 
of files required for a common purpose. Each resource can be part of
multiple datasets, so the same reference can be used in multiple 
contexts.

Installation
------------

To install datahub, you need to load its dependencies. For that, you 
may want to create a virtualenv before you perform these steps::
  
  pip install -r pip-requirements.txt
  pip install -e .

To configure datahub, create a copy of datahub/default_settings.py with
appropriate configuration settings. When starting datahub, set the
environment variable DATAHUB_SETTINGS to the path of your local config
file.

You also need to make sure that an elastic search daemon is running at 
the location specified in your configuration file. Elastic search is 
required even if you just want to run the tests.

If you also want to run asynchronous tasks, you will need to create 
a file called `celeryconfig.py`, normally by symlinking either to your
local configuration or to `datahub/default_settings.py`. 


