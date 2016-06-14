aws_scripts
===========

Installation
------------

To install

    git clone <repo>
    cd <repo>

System wide

    sudo pip install .

Virtual environment

    virtualenv env
    source env/bin/activate
    pip install --editable .
    

r53
---

Mainly used to set the weight of load balanced RR's.

For example:

    r53 set weight -pz -s '-frontlb01' 0 example.com www api

Would be used to set the records www.example.com and api.example.com to 0 for
the weighted RR's with the SetIdentifiers of www-frontlb01 and api-frontlb01.
