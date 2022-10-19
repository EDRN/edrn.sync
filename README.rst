.. note::
    🛑 The functions provided by this package are now part of https://github.com/EDRN/jpl.edrn.ldap.sync

This is the EDRN Sync Services (EDRN_) Client package.  It provides an API
for slurping up the DMCC RDF user stream from their identity management 
system.  It also provides the following command-line tools:

dmccsync
    Takes a DMCC RDF users file and imports it into the EDRN IC LDAPS server.
dmccgroupsync
    Takes a DMCC RDF users file and a sites file and imports the associated
    PI groups and collaborative groups into the EDRN IC LDAPS server.
secureoldpasswords
    Randomizes users given a default insecure password by ``dmccsync``.


For installation instructions, please see docs/INSTALL.txt.

This is licensed software; please see docs/LICENSE.txt.

For the latest news and changes, see docs/HISTORY.txt.

.. References:
.. _EDRN:   https://edrn.nci..nih.gov/
