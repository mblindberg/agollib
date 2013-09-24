""" GetSiteUsers.py
    Creates an Excel-readable CSV file containing basic information on all users for
    the ArcGIS Online site.
"""
import agollib

OUTNAME = "users.csv"

def getRatio(a, b, precision=7, percent=False):
  """Returns ratio of two numbers (longs) as a formatted string; caller may specify precision
  and if result should be a percentage."""
  if b == 0:                 # kluge: must fix
    b = float(0.00001)
  result = float(a) / float(b) * 100 if percent else float(a) / float(b)
  fmt = "{:0."+str(precision)+"f}"
  return fmt.format(result)

def getUsers():
  """Writes basic information about users to a CSV file."""
  token = agollib.getToken()[0]
  siteInfo = agollib.SubscriptionProperties(token)
  results = siteInfo.getUsers(token)
  space = siteInfo.storage
  with open(OUTNAME,'w') as f:
    f.write('"USERNAME","ROLE","USAGE","QUOTA","PCTQUOTA","PCTSITEUSE","PCTSITEQUOTA"'\
            ',"CREATED","MODIFIED","FULLNAME","EMAIL"\n')
    
    for user in results:
      f.write("\""+user[u'username']+"\","+
              "\""+user[u'role']+"\","+
              str(user[u'storageUsage'])+","+
              str(user[u'storageQuota'])+","+
              getRatio(user[u'storageUsage'], user[u'storageQuota'], percent=True)+","+
              getRatio(user[u'storageUsage'], space[0], 4, True)+","+
              getRatio(user[u'storageUsage'], space[1], 5, True)+","+
              agollib.getDateTime(user[u'created'])+","+
              agollib.getDateTime(user[u'modified'])+","+
              "\""+user[u'fullName']+"\","+
              "\""+user[u'email']+"\"\n")
      
  f.close()
  print "Basic user stats written to", OUTNAME
  return

if __name__ == "__main__":
  getUsers()

  
