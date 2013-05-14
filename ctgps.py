import xml.dom.minidom as md
import time as _time
import datetime
from math import sin,cos, sqrt, hypot, radians, atan2

def GPS_DIST(wp1,wp2):
    """wp format: (lat,lon) as decimal degrees"""
    R = 6371000 #avg radius of earth in meters
    lon1 = radians(wp1[1])
    lon2 = radians(wp2[1])
    lat1 = radians(wp1[0])
    lat2 = radians(wp2[0])
    dlat = lat1-lat2
    dlon = lon1-lon2
    #sq of half the chord length
    a = sin(dlat/2)*sin(dlat/2)+cos(lat1)*cos(lat2)*(sin(dlon/2)*sin(dlon/2))
    # angular distance in radians
    c = 2*atan2(sqrt(a),sqrt(1-a))
    # dist
    return R*c

def parse_GPRMC(s):
    CS = int(s[-2:],16)
    if CS != checksum(s[1:-3]):
        print 'CS FAIL!'
        return None
    
    d = RMCdat()
    litems = s.split(',')
    #check valid data
    if litems[2] != 'A':
        return None
    time_stamp = litems[1]
    hr = int(time_stamp[0:2])
    mins = int(time_stamp[2:4])
    sec = int(time_stamp[4:6])
    usec = int(time_stamp[7:10])*1000
    lat = litems[3]
    lon = litems[5]
    #convert to degrees
    latd = int(lat[:-7])+float(lat[-7:])/60.0
    lond = int(lon[:-7])+float(lon[-7:])/60.0
    #add sign
    if litems[4]=='S':
        latd = -latd
    if litems[6]=='W':
        lond = -lond
    d.lat = latd
    d.lon = lond
    #speed in kph
    d.speed = float(litems[7])*1.852
    #date
    datestamp = litems[9]
    day = int(datestamp[0:2])
    month = int(datestamp[2:4])
    year = int(datestamp[4:])+2000
    #fill in datetime object
    d.dtime = datetime.datetime(year,month,day,hr,mins,sec,usec)
    
    return d

def checksum(s):
    f =map(ord,s)
    cs = 0
    for q in f:
        cs = cs ^q
    return cs

def parse_waypoints(file_name):
    """ returns an ordered list of waypoints from a gpx file file_name"""
    tree = md.parse(file_name)
    assert tree.documentElement.tagName == 'gpx'
    route = tree.getElementsByTagName('rte')[0]
    #TODO: check above succeeds 

    wp_list = []
    for rpoint in route.getElementsByTagName('rtept'):
        
        #print rpoint.getElementsByTagName('name')[0].nodeName
        #print rpoint.getElementsByTagName('name')[0].firstChild.nodeValue
        assert rpoint.hasAttributes()
        coord = (float(rpoint.getAttribute('lat')),
                 float(rpoint.getAttribute('lon')) )
        wp_list.append(coord)
        #print 'lat: ' + rpoint.getAttribute('lat') + \
        #      ', lon: ' + rpoint.getAttribute('lon')
    return wp_list

def latlon2rect(origin,gpspoint):
    """Convert a gpspoint to rectangular coords, where the origin is the gps location of (0,0)"""
    dx = GPS_DIST(origin,(origin[0],gpspoint[1])) #change only in x
    dy = GPS_DIST(origin,(gpspoint[0],origin[1])) #change only in y
    
    if gpspoint[1] < origin[1]:
        dx = -dx
    if gpspoint[0] < origin[0]:
        dy = -dy
    
    return (dx,dy )

def _project(A, B):
    """ Length of A's component in B direction (ie A.B/||B||)"""
    Blen = _vlen(B)
    Bn = (B[0]/Blen, B[1]/Blen)  #normalize vector B
    return (A[0]*Bn[0]+A[1]*Bn[1])

def _vlen(B):
    """return length of 2d vector B"""
    return sqrt(B[0]*B[0]+B[1]*B[1])
    
def _dist(A,B):
    return hypot(A[0]-B[0],A[1]-B[1])



############# DATA TYPES #######################
class RMCdat:
    def __init__(self):
        self.dtime = None
        self.speed = 0.0
        self.lon = 0.0
        self.lat = 0.0
    
    def getepochtime(self):
        if self.dtime ==None:
            return None
        return (_time.mktime(self.dtime.timetuple())+
                    self.dtime.microsecond/1000000.0)
        
        
    
class Chord:
    """
    Defines a chord specified by two points p1, p2 defined by (x,y)
    note: p1 should always be closer (by driving distance) than p2
    """
    
    def __init__(self,p2):
        self.p1 = (0,0)
        self.p2 = p2

    def __init__(self,p1,p2):
        self.p1 = p1
        self.p2 = p2

    def closest(self,p):
        """ returns the closest point on the chord to p """
        
        a = _vlen((self.p1[0]-self.p2[0],self.p1[1]-self.p2[1]))
        b = _vlen((self.p1[0]-p[0],self.p1[1]-p[1]))
        c = _vlen((p[0]-self.p2[0],p[1]-self.p2[1]))
        
        #is the closest point on the line?
        if (a*a+b*b>c*c) and (a*a+c*c>b*b):
            line_p_p1 = (self.p1[0]-p[0],self.p1[1]-p[1])
            v_orth = (self.p1[1]-self.p2[1],-self.p1[0]+self.p2[0])
            v_orth_norm = (v_orth[0]/_vlen(v_orth), v_orth[1]/_vlen(v_orth))
            dist = _project(line_p_p1, v_orth_norm)
            return (v_orth_norm[0]*dist+p[0],v_orth_norm[1]*dist+p[1])
        else:
            if b<c:
                return self.p1
            else:
                return self.p2
            
    def length(self):
        return _dist(self.p1,self.p2)


class ClosedPath:
    def __init__(self, points):
        self.chords = []
        for i in range(len(points)):
            j = i+1
            if j == len(points):
                j = -1
            self.chords.append(Chord(points[i],points[j]))
        
    def closest(self,p):
        """returns the closest point on path to p"""
        min_coord = self.chords[0].closest(p)
        min_dist = _dist(p,min_coord)
        for c in self.chords:
            coord = c.closest(p)
            if min_dist > _dist(p,coord):
                min_dist = _dist(p,coord)
                min_coord = coord
        
        return min_coord
        
    def driving_distance(self,p):
        """returns the driving distance between p and Start/Finish point """
        min_coord = self.chords[0].closest(p)
        min_dist = _dist(p,min_coord)
        #length from min_coord to SF line
        l = _dist(min_coord,self.chords[0].p1) 
        pl = 0 #length of all previous chords
        for c in self.chords:
            coord = c.closest(p)
            if min_dist > _dist(p,coord):
                min_dist = _dist(p,coord)
                min_coord = coord
                l = pl+_dist(coord,c.p1)
                #print "----" + str(l)
            pl = pl+c.length()
        return l
