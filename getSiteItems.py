""" GetSiteItems.py
    Creates an Excel-readable CSV file containing basic information on all user-created
    data for the ArcGIS Online site.
"""
import agollib

def getSiteItems():
  """Writes basic statistics about all user-owned items to a CSV file."""
  outfile = "items.csv"
  token = agollib.getToken()[0]
  siteInfo = agollib.SubscriptionProperties(token)
  results = siteInfo.getItems(token)
  with open(outfile,'w') as f:
    f.write('"OWNER","TITLE","TYPE","ID","SIZE","ACCESS","CREATED","MODIFIED"\n')
    for itemId in results:
      item = results[itemId]
      f.write("\""+item[u'owner']+"\","+
              "\""+item[u'title']+"\","+
              "\""+item[u'type']+"\","+
              "\""+item[u'id']+"\","+
              str(item[u'size'])+","+
              "\""+item[u'access']+"\","+
              agollib.getDateTime(item[u'created'])+","+
              agollib.getDateTime(item[u'modified'])+"\n")

  f.close()
  print "Basic stats on", len(results), " items written to", outfile
  return results

if __name__ == "__main__":
  z = getSiteItems()
