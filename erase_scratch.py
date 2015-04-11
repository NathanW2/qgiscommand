__author__ = 'Antonio'

def DMS (lat, lon):
    """
    Add a point at the lat and lon for the current layer using DMS notation
    """
#lat = raw_input('lat: ')
#lon = raw_input ('lon: ')

lat = '14 34 24 n'
lon = '087 34 23 w'



l_lat = lat.upper().split()
l_lon = lon.upper().split()

if l_lat[3] == 'N':
    ddlat = float(l_lat[0])+float(l_lat[0])/60+float(l_lat[0])/3600
elif l_lat[3] == 'S':
    ddlat = (float(l_lat[0])+float(l_lat[0])/60+float(l_lat[0])/3600)*-1
else:
    ddlat = '0'

if l_lon [3] == 'E':
    ddlon = float(l_lon[0])+float(l_lon[0])/60+float(l_lon[0])/3600
elif l_lon[3] == 'W':
    ddlon = (float(l_lon[0])+float(l_lon[0])/60+float(l_lon[0])/3600)*-1
else:
    ddlon = '0'

print ddlat,ddlon


    #lat,lon = float(lat), float(lon)

