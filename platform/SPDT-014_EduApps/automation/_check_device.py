# coding: utf-8
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xdevice import Variables
print("hypium device check OK, device_sn:", getattr(Variables.config, 'device_sn', 'check config'))
