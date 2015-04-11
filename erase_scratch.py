__author__ = 'Antonio'

def DMS (lat, lon):
    """
    Add a point at the lat and lon for the current layer using DMS notation
    """
#lat = raw_input('lat: ')
#lon = raw_input ('lon: ')

lat = '14 03 36.92 n'
lon = '087 13 02.68 w'



l_lat = lat.upper().split()
l_lon = lon.upper().split()

print l_lat
print l_lon

if l_lat[3] == 'N':
    ddlat = float(l_lat[0])+(float(l_lat[1])/60)+float(l_lat[2])/3600
elif l_lat[3] == 'S':
    ddlat = (float(l_lat[0])+float(l_lat[1])/60+float(l_lat[2])/3600)*-1
else:
    ddlat = '0'

if l_lon [3] == 'E':
    ddlon = float(l_lon[0])+float(l_lon[1])/60+float(l_lon[2])/3600
elif l_lon[3] == 'W':
    ddlon = (float(l_lon[0])+float(l_lon[1])/60+float(l_lon[2])/3600)*-1
else:
    ddlon = '0'

print ddlat,ddlon


    #lat,lon = float(lat), float(lon)

