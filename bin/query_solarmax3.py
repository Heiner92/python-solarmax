#!/usr/bin/python
# -* coding: utf-8 *-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Developed 2009-2010 by Bernd Wurst <bernd@schokokeks.org> 
# for own use.
# Released to the public in 2012.


import time, sys, os
from solarmax3 import SolarMax

''' 
not using any DataBase for testing purposes
'''

#from sqlite3 import dbapi2 as sqlite
#DB_FILE=sys.argv[1]
#dbconn = sqlite.connect(DB_FILE)
#db = dbconn.cursor()

# Zeitinterval in Sekunden 
# (in welchem zeitlichen Abstand werden die Werte von den WR ausgelesen)
query_interval = 2
inverters = { '192.168.0.201': [1,],
              '192.168.0.202': [2,],
              '192.168.0.203': [3,],
              '192.168.0.204': [4,],
            }


smlist = []
for host in inverters.keys():
  sm = SolarMax(host, 12345)
  sm.use_inverters(inverters[host])
  smlist.append(sm)


allinverters = []
for host in inverters.keys():
  allinverters.extend(inverters[host])



while True:
  pac_gesamt = 0.0
  daysum_gesamt = 0.0

  count = 0
  for sm in smlist:
    for (no, ivdata) in sm.inverters().items():
      try:
        (inverter, current) = sm.query(no, ['PAC', 'KDY', 'KT0', 'IDC', 'UDC', 'IL1', 'UL1', 'FDAT', 'SYS'])
        count += 1
      except:
        # Kommunikationsfehler, evtl. Wechselrichter aus
        print('Kommunikationsfehler, WR {}'.format(no))
        continue
    
      ivmax = ivdata['installed']
      ivname = ivdata['desc']
      PAC_calc = current['IL1'] * current['UL1']
      PAC_read = current['PAC']
      percent = int((PAC_read/ivmax) * 100)
      PDC_calc = current['IDC'] * current['UDC']
      (status, errors) = sm.status(no)
      if errors:
        print('WR {}: {} ({})'.format(no, status, errors))
      

      print('''
      WR {} ({})
        Status: {}
        Aktuell: {:9.1f} Watt / errechnet: {:8.1f} W ({} % von {} Watt)
        P_DC:    {:9.1f} Watt (Wirkungsgrad: {} %)
        Gesamt heute:   {:8.1f}   kWh
        Gesamt bisher:  {:8.1f}   kWh (seit {})
      '''.format(inverter, 
        ivname, 
        status, 
        PAC_read, 
        PAC_calc, 
        percent, 
        ivmax, 
        PDC_calc, 
        int((float(PAC_calc)/PDC_calc) * 100), 
        current['KDY'],
        current['KT0'], 
        current['FDAT'].date()))
#      try:
#        # Könnte gelocked sein
#        # System ist 2 in diesem Fall. Fix.
#        db.execute('''INSERT INTO performance (time, inverter, system, pac, daysum, total) VALUES (strftime('%%s','now'), %i, 2, %i, %i, %i)'''
#                  % (inverter, int(current['PAC']), int(current['KDY']*1000), int(current['KT0']*1000)))
#      except:
#        pass
      pac_gesamt += current['PAC']
      daysum_gesamt += current['KDY']
#  try:
#    dbconn.commit()
#  except:
#    pass
  if count < len(allinverters):
    print('Zu wenig Wechselrichter ({} < {})'.format(count, len(allinverters)))

  #print '='*80
  #print 'GESAMT:  %9.2f Watt    / Heute: %8.1f kWh' % (pac_gesamt, daysum_gesamt)
  time.sleep(query_interval)








