import psycopg2
import csv
import subprocess

# T.Carman Dec 2019, Jan 2020
# Idea is to export a bunch of info about priors from bety DB into a table that
# can be included in the manuscript.


con = psycopg2.connect(database="bety", user="bety", password="", host="localhost",)
cur = con.cursor()

cur.execute("""SELECT * FROM pfts_priors WHERE pft_id IN (SELECT id FROM pfts WHERE name LIKE 'CMT04-%');""")
rows = cur.fetchall()

everything = []
for (pftid, prid,cdate,udate,ppid) in rows:
  print pftid, prid, cdate, udate, ppid
  
  cur.execute("""SELECT name FROM pfts WHERE id IN ({});""".format(pftid))
  pftname = cur.fetchall()[0] # Should be only one record returned
  
  cur.execute("""SELECT variable_id from priors WHERE id in ({});""".format(prid))
  vid = cur.fetchall()[0] # Should be only one record returned

  cur.execute("""SELECT name FROM variables WHERE id in ({});""".format(vid[0]))
  vname = cur.fetchall()[0] # Should be only one record returned

  cur.execute("""SELECT distn, parama,paramb,n FROM priors WHERE id in ({});""".format(prid))
  prior_stuff = cur.fetchall()[0]


  #distname,parama,paramb,n = prior_stuff
  a = dict(pftname=pftname[0], distname=prior_stuff[0], parama=prior_stuff[1], paramb=prior_stuff[2], N=prior_stuff[3], vname=vname[0])
  print a
  everything.append(a)


#retCode = subprocess.checkcall(["./prior_stats_image.R", shell=True])
  

with open("/tmp/somejunk.txt", 'w') as f:
  dw = csv.DictWriter(f, everything[0].keys())
  dw.writeheader()
  for i in everything:
    dw.writerow(i)

con.close()

!less /tmp/somejunk.txt



