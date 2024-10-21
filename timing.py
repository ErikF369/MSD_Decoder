'''
Created on 09.10.2024

@author: efrank
'''
import datetime

Zahl = 2893137983832
Zahl_in_sekunden = Zahl / 1000
datum = datetime.datetime.utcfromtimestamp(int(Zahl_in_sekunden))

print(datum)