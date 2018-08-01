#!/bin/bash

nohup python getGWSecurityState.py > /dev/null 2>&1&
nohup python getSirenState.py > /dev/null 2>&1&
ps aux | grep python
