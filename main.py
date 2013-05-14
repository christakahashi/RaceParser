from ctgps import *
import pygame
import sys
import datetime
import os

#parameters
track_map = 'infineon_day_1.gpx'
gps_data_path = 'C:\users\chris\Desktop\gpslog.txt'

#Some globals

black = 0, 0, 0
white = 255,255,255
yellow = 255,255,0
green = 0,255,0
blue = 0,0,255

#the track map limits in meters
lmin = (-800,-300)
lmax = (800,700)

#test_locs = [(x,-3*x/5+140) for x in range(-600,400,50)]

def init_state():
    #get waypoints as GPS coords
    wplst_gps = parse_waypoints(track_map)
    #get waypoints as X,Y in meters, from SF line.
    origin = wplst_gps[0]
    wplist = [latlon2rect(origin,p) for p in wplst_gps]
    trackpath = ClosedPath(wplist)
    print 'done with parser!'
    
    #setup window stuff
    s = empty_struct() #for storing state
    s.win = pygame.display.set_mode((800,600))
    s.clk = pygame.time.Clock()
    s.track_poly = wplist
    s.font = pygame.font.SysFont(None,24)
    s.corner_txt = ''
    s.trackpath = trackpath
    s.dot = (0,0)
    s.origin = origin
    
    return s

def parse_gps_data(s,file_name):
    inf = open(file_name,'rb')
    file_size = os.path.getsize(file_name)
    lines = inf.readlines()
    inf.close()
    start_time = None
    ofs = open('out.dat','w')
    ddx = 0
    count = 0
    for line in lines:
        line = line.strip()
        tokens = line.split()
        if line.startswith('$GPRMC'):
            msg = parse_GPRMC(line)
            if msg !=None:
                point = latlon2rect(s.origin,(msg.lat,msg.lon))
                d = s.trackpath.driving_distance(point)
                rectcoord = latlon2rect(s.origin,[msg.lat, msg.lon])
                
                st = '%.3f, %.2f, %.2f, %s, %.2f, %.2f\n' % (msg.getepochtime(),d, msg.speed,ddx,rectcoord[0],rectcoord[1])
                ofs.write(st)
        if len(tokens)>3 and tokens[1]=='ddx:':
            #x accel data
            ##print tekens[2]
            ddx = tokens[2]
        if count%10000 == 0:
            status(count*100/len(lines))
        count = count+1
            
    ofs.close()
                
                
def status(percent):
    sys.stdout.write("%3d%%\r" % percent)
    sys.stdout.flush()
    
    
def main():
    bb = Chord((1,0),(0,1))
    print bb.closest((1,1))
    s = init_state()
    parse_gps_data(s,gps_data_path)
    while 1:
        s.win.fill(black)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    left_click(s,event.pos)
            elif event.type ==pygame.MOUSEMOTION:
                move_mouse(s,event.pos)
            else: print event
        ##run graphics loop
        s = graphics_loop(s)
        pygame.display.flip()
        s.clk.tick(60)
    

def graphics_loop(s):
    #take care of text
    ctxt = s.font.render(s.corner_txt,True,white)
    s.win.blit(ctxt,ctxt.get_rect())
    dottxt = s.font.render('dot:'+str(s.dot),True,white)
    s.win.blit(dottxt,dottxt.get_rect().move(0,20))
    #compute polynomial 
    tpoly_s = [xy2scrnxy(p,s.win,lmin,lmax) for p in s.track_poly]
    pygame.draw.polygon(s.win,white,tpoly_s,2)
    #draw Start/Finish point
    pygame.draw.circle(s.win,blue,tpoly_s[0],6)
    #draw cursor dot
    pygame.draw.circle(s.win,green,xy2scrnxy(s.dot,s.win,lmin,lmax),6)
    
    #some testing stuff
    #pygame.draw.line(s.win,green,xy2scrnxy(test_locs[-1],s.win,lmin,lmax),
    #                 xy2scrnxy(test_locs[0],s.win,lmin,lmax))
    #for p in test_locs:
    #    pygame.draw.line(s.win,yellow,xy2scrnxy(p,s.win,lmin,lmax)
    #                     ,xy2scrnxy(s.trackpath.closest(p),s.win,lmin,lmax))
    
    return s

def left_click(s,p):
    p_xy = scrnxy2xy(p,s.win,lmin,lmax)
    s.corner_txt = str(p_xy) + str(s.trackpath.driving_distance(p_xy))
    print str(p)+ "->" + str(p_xy)
    
def move_mouse(s,p):
    d = scrnxy2xy(p,s.win,lmin,lmax)
    s.dot = s.trackpath.closest(d)
    
        
################HELPER FNS##################################

def scrnxy2xy(p,win,lim_min,lim_max):
    x = p[0]
    y = p[1]
    new_x = x*(lim_max[0]-lim_min[0])/win.get_width()+lim_min[0]
    y = win.get_height()-y #unflip
    new_y = y*(lim_max[1]-lim_min[1])/win.get_height()+lim_min[1]
    return (new_x,new_y)
   
def xy2scrnxy(p,win,lim_min,lim_max):
    """
    returns the screen coordinate given the (x,y) coord p
    win is the window to draw in and lim_max=(xmax,ymax)
    """
    x = p[0]
    y = p[1]
    new_x = win.get_width()*(x-lim_min[0])/(lim_max[0]-lim_min[0])
    new_y = win.get_height()*(y-lim_min[1])/(lim_max[1]-lim_min[1])
    new_y = win.get_height()-new_y #flip 
    return (int(round(new_x)),int(round(new_y)))


class empty_struct:
    pass

if __name__ == '__main__':
    pygame.init()
    main()
