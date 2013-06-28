""" 
This script is a template for local information used by agollib.
Fill out this script appropriately and rename it Local.py.
Three constants must be filled in: MD5HASH, HOSTNAME, and ORGID.  USER and
PASS should normally be set to None.  If, however, USER and PASS are set to
their actual appropriate values, scripts employing agollib will not query for
account name and password at runtime.

IMPORTANT: Do not change Local.Template.py unless you are contributing a change
to the agollib project.

IMPORTANT: Do not add your Local.py to git!  Do not push Local.py to GitHub!
Especially if you fill in your administrative account name and password!!!

Author:        mbl - mbl@umn.edu: Mark Lindberg
Contributers:

Notes on constants:
    
  USER:     None or name of local administrative account.  
              If set to None, agollib.getToken will query for account name at 
              runtime.  Best practice is to keep this None.
  PASS:     None or password for USER.  
              If set to None, agollib.getToken will query for password at 
              runtime (using  getpass library, so password will not be displayed
              on screen).  Best practice is to keep this None.
  MD5HASH:  USER's password md5hash.
              PASS is always checked against this hash.  If a match is not 
              found, the hash for the input password is displayed.  Hence, to
              set up for your account, simply run a script using agollib and 
              then copy and paste the reported hash to this file.
  HOSTNAME: Site name assigned to your subscription by Esri.
  ORGID:    ID assigned to your subscription by Esri.

"""


USER =     None
PASS =     None
MD5HASH =  "00000000000000000000000000000000"
HOSTNAME = "xxxxxxxxx.arcgis.com"
ORGID =    "9999999999"
