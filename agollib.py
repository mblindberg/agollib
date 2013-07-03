"""
agollib: A library of routines for working with ArcGIS REST API.

  REQUIRES: Requests library that is used to manage HTTP requests
  USES:     getpass, hashlib, socket, sys, and time standard libraries


Author:        mbl - mbl@umn.edu: Mark Lindberg
Contributers:

Notes:

"""
import getpass, socket, sys, time, requests, hashlib  #, json
import Local

VERBOSE = True

class SubscriptionProperties:
  """Information about organization resources. Must be administrator to obtain."""

  PORTALPATH = "/sharing/rest/portals/"+Local.ORGID
  RESOURCESPATH = PORTALPATH+"/resources"
  USERSPATH = PORTALPATH+"/users"
  SEARCHPATH = "/sharing/rest/search"
  VERSIONPATH = "/sharing/rest"
  COMMUNITYPATH = "/sharing/rest/community"
  CONTENTPATH = "/sharing/rest/content"
  USERSCONTENTPATH = CONTENTPATH+"/users"

  def __init__(self, token):
    self.results = getQueryResponse(self.PORTALPATH, {'token': token})
    self.storage = self.__storage()
    self.availableCredits = self.__availableCredits()
    self.agolVersion = self.__currentVersion()
    self.resourceList = []
    self.userList = []
    self.groupList = []
    self.itemList = []
    return

  def getResources(self, token):
    """ holder """
    def getParams(i):
      """ holder """
      return {'token': token, 'start': str(i), 'num': '10'}
    ndx = 1
    while ndx > 0:
      temp = getQueryResponse(self.RESOURCESPATH, getParams(ndx))
      for resource in temp['resources']:
        self.resourceList.append(resource)
      ndx = temp['nextStart']
    return self.resourceList
  
  def getUsers(self, token):
    """Returns a list of all user dictionaries reported by portal/users; A list of usernames
    is kept in userList."""
    def getParams(i):
      """ holder """
      return {'token': token, 'start': str(i), 'num': '100'}
    ndx = 1
    userInfo = []
    while ndx > 0:
      temp = getQueryResponse(self.USERSPATH, getParams(ndx))
      for user in temp['users']:
        self.userList.append(user['username'])
        userInfo.append(user)
      ndx = temp['nextStart']
    return userInfo
 
  def getGroups(self, token):
    """Returns a dictionary of all groups ( id: (title,owner))."""
    basePath = self.COMMUNITYPATH+'/users'
    if len(self.userList) < 1:
      self.getUsers(token)
    params = { 'token': token }
    groups = []
    groupDict = {}
    for user in self.userList:
      path = basePath+"/"+user
      results = getQueryResponse(path, params)
      groups.append(results[u'groups'])
    for i in range(len(groups)):
      for j in range(len(groups[i])):
        g = groups[i][j]
        groupDict[g[u'id']] = (g[u'title'], g[u'owner'])
    for i in groupDict.keys():
      self.groupList.append(i)
    return groupDict

  def getItems(self, token):
    """Returns a dictionary of item data with item IDs as keys."""
    itemDict = {}
    if len(self.userList) < 1:
      self.getUsers(token)
    params = { 'token': token }
    for user in self.userList:
      path = self.USERSCONTENTPATH+"/"+user
      results = getQueryResponse(path, params)
      nFolders = len(results[u'folders'])
      userFolders = []
      if nFolders > 0:
        for folder in range(len(results[u'folders'])):
          userFolders.append((results[u'folders'][folder][u'id'], 
                              results[u'folders'][folder][u'title']))
      r = results[u'items']
      if len(r) > 0:
        for item in range(len(results[u'items'])):
          itemDict[r[item][u'id']] = r[item]
      for folder in userFolders:
        path = self.USERSCONTENTPATH+"/"+user+"/"+folder[0]
        results = getQueryResponse(path, params)
        r = results[u'items']
        if len(r) > 0:
          for item in range(len(results[u'items'])):
            itemDict[r[item][u'id']] = r[item]
    for i in itemDict:
      self.itemList.append(i)
    return itemDict

   
  def __storage(self):
    """Returns a tuple with current storage usage in bytes and current storage quota in bytes."""
    usedKey = u'storageUsage'
    quotaKey = u'storageQuota'
    checkKey(usedKey, self.results)
    checkKey(quotaKey, self.results)
    return((long(self.results[usedKey]), long(self.results[quotaKey])))
    
  def __availableCredits(self):
    """Returns currently available credits for the portal."""
    creditKey = u'availableCredits'
    checkKey(creditKey, self.results)
    return (float(self.results[creditKey]))

  def __currentVersion(self):
    """Returns current version number for ArcGIS Online."""
    results = getQueryResponse(self.VERSIONPATH, {})
    checkKey(u'currentVersion', results)
    return results[u'currentVersion']

  def expirationDate(self):
    """Returns formatted expiration date."""
    key = u'expDate'
    subInfo = self.subscriptionInfo()
    checkKey(key, subInfo)
    return getDateTime(subInfo[key])

  def subscriptionInfo(self):
    """Returns a dictionary with basic subscription information."""
    key = u'subscriptionInfo'
    checkKey(key, self.results)
    return self.results[key]

  def search(self, token, queryString):
    """Simple search utility. Returns a dictionary with query string, total number of hits,
       and results."""
    def getParams(i):
      """ holder """
      return {'q': queryString, 'token': token, 'start': str(i), 'num': '100'}
    ndx = 1
    searchResults = []
    while ndx > 0:
      temp = getQueryResponse(self.SEARCHPATH, getParams(ndx))
      for results in temp['results']:
        searchResults.append(results)
      ndx = temp['nextStart']
    return {'query': temp['query'], 'total': temp['total'], 'results': searchResults}


  def dumpAll(self):
    """Used for testing; to be removed."""
    for i in sorted(self.results.keys()):
      if type(self.results[i])=='dict':
        for j in sorted(self.results[i].keys()):
          print "     ", i, j, type(self.results[i][j]), self.results[i][j]
      elif type(self.results[i])=='list':
        for j in self.results[i]:
          print "     ", i, j, type(self.results[i][j]), self.results[i][j]
      else:
        print i, type(self.results[i]), self.results[i]
    return
  
# ================================ end of class =========================================

def checkKey(key, dictionary):
  """Determines if key (k) is found in dictionary (r); stops script if not found."""
  if key not in dictionary:
    print "Error:", key, "not found in", dictionary
    sys.exit(1)
  return(True)

def getQueryResponse(path, params):
  """
  Primary driver routine for working with ArcGIS Portal API. Uses requests library to make queries.
    Input Parameters: path: string: path part of REST URI
                      params: dictionary: data part of call (note that specifying json output is always appended)
    Returns: response: dictionary: contains returned property name - results pairs
  """
  timeOut = 30
  protocol = "https"
  
  url = protocol+"://"+Local.HOSTNAME+path
  params['f'] = 'json'
  try:
    response = requests.post(url, params, timeout=timeOut, verify=True)
  except requests.exceptions.HTTPError:
    print "HTTP error"
    sys.exit(1)
  except requests.exceptions.ConnectionError:
    print "Network error"
    sys.exit(1)
  except requests.exceptions.Timeout:
    print "Timeout"
    sys.exit(1)
  except requests.exceptions.RequestException:
    print "Unknown error"
    sys.exit(1)
  if response.status_code == '200':
    print "Status Code: ", response.status_code
    sys.exit(1)
  if (u'error' in response.json()):
    print "Error:", response[u'error'][u'message']
    if VERBOSE: print response  # pylint: disable-msg=C0321
    sys.exit(1)
  return response.json()

def decodeMillisecondTime(xTime):
  """Convert time in miliseconds since the epoch to a struct_time object."""
  return time.localtime(float(xTime) / 1000)

def timeStr(timeObject):
  """Convert a struct_time object to a string using the format set by DATETIMEFORMAT."""
  dateTimeFmtStr = "%Y-%m-%d %H:%M:%S"  # 2012-03-26 17:38:44
  #dateTimeFmtStr = "%Y-%m-%dT%H:%M:%S"  # 2012-03-26T17:38:44
  #dateTimeFmtStr = "%a, %d-%b-%y %I:%M%p"  # Tues, 10-JUL-12 11:18AM
  return time.strftime(dateTimeFmtStr, timeObject)

def getDateTime(esriTimeObject):
  """Use for decoding date-times reported by Esri."""
  return timeStr(decodeMillisecondTime(esriTimeObject))

def getToken():
  """
  Generates an access token for working with the ArcGIS Portal API. Returns a token plus
  an expiration time (milliseconds since Jan 1, 1970).
  Prompts the user for a username and password. The password is checked against an md5 hash and
  if it does not match the script exits -- displaying the hash for the entered password. This
  allows the user to modify the script (MD5HASH) to match their password.
  """
  expireTime = "30"
  tokenKey = u'token'
  expiresKey = u'expires'
  tokenPath = "/sharing/generateToken"

  clientIP = socket.gethostbyname(socket.gethostname())

  if Local.USER is None or Local.PASS is None:
    userName = raw_input("User Name: ")
    passWord = getpass.getpass()
  else:
    userName = Local.USER
    passWord = Local.PASS

  pw = hashlib.md5()
  pw.update(passWord)
  if pw.hexdigest() != Local.MD5HASH:
    print "Unknown password -- md5hash:", pw.hexdigest()
    print "To use your password, copy and paste the md5hash into Local.py."
    sys.exit(1)
    
  params = { 'username': userName,
             'password': passWord,
             'expiration': expireTime,
             'client': "referer",
             'referer': clientIP }

  response = getQueryResponse(tokenPath, params)
  checkKey(tokenKey, response)
  checkKey(expiresKey, response)
  return (response[u'token'], response[u'expires'])


if __name__ == "__main__":
  (TOKEN, EXPIRETIME) = getToken()
  x = SubscriptionProperties(TOKEN)
  print x.agolVersion
  print TOKEN
 
  
