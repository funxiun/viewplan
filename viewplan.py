#!/usr/bin/env python
# -*- coding: utf-8 -*- 
                          
"""
Use the PyEphem package to develop a plan for an evening's stargazing.
"""       

import re
import sys
import math
import time
import argparse
import itertools 

import parsedatetime
from ephem import *      

# Our data sets are in EDB format, described here:
# https://www.mmto.org/obscats/edb.html

def describe_body( subfields ):
    # Map the edb format type-subfield codes to presentable text
    if subfields[0] == 'P':
        return "planet"
    if subfields[0] == 'E':
        return "satellite"
    if subfields[0] in 'ehp':
        return "planetoid"
        
    FIXED_BODY_MAP = {
        'A' : "cluster of galaxies",
        'B' : "binary star",
        'C' : "globular cluster",
        'D' : "visual double star",
        'F' : "diffuse nebula",
        'G' : "spiral galaxy",
        'H' : "spherical galaxy",
        'J' : "radio object",
        'K' : "dark nebula",
        'L' : "pulsar",
        'M' : "multiple star",
        'N' : "bright nebula",
        'O' : "open cluster",
        'P' : "planetary nebula",
        'Q' : "quasar",
        'R' : "supernova remnant",
        'S' : "star",
        'T' : "stellar object",
        'U' : "nebulous cluster",
        'V' : "variable star",
        'Y' : "supernova"     }            
        
    if subfields[0] == 'f':
        return FIXED_BODY_MAP[subfields[1]]  
        
    return "?"    

def read_database( filename ):
    # Read a set of bodies from an EDB file. 
    bodies = []
    desc = {}   
    dbpath = "databases/"
 
    # Read the file.
    with open(dbpath + filename) as f:
        # Look at each line of the file
        for line in f:
            line=line.strip()
        
            # Skip comments
            if line.startswith('#'):
                continue    
            
            # Skip malformed lines
            if "," not in line:
                continue              

            # Split the line apart.
            elements = line.split(",") 
            # Extract the name
            name = elements[0]
            # Extract the type fields
            subfields = elements[1].split('|') 
            # Map those to a description
            desc = describe_body(subfields)  
            
            # Give the whole line to pyephem
            body = readdb(line)

            bodies.append( (desc,body) )
        
    return bodies

def messier_candidates():    
    # Read the Messier catalog for DSO candidate targets.
    return read_database( "Messier.edb" )

def ngc_candidates():
    # Read the Messier catalog for DSO candidate targets.
    return read_database( "NGC.edb" )


def star_candidates():                                                                           
    # Read the star catalog, but reject those whose description is simply 
    # "star" as opposed to "binary star", "variable star" etc.
    return [(desc,body) for (desc,body) in read_database( "SKY2k65.edb" ) if desc != "star"]
 
def planet_candidates():    
    # Planets and Earth's moon are built into ephem, so just return those directly
    return  [  ("planet", Jupiter() ),
               ("planet", Mars()   ),
               ("planet", Saturn() ),
               ("planet", Venus()  ), 
               ("planet", Uranus() ),
               ("planet", Neptune()),
               ("moon"  , Moon()   )   ]         

def body_in_altitude_range( body, minAlt, maxAlt ):
    # Returns true if the body's altitude is within the specified min and max. 
    # PyEphem body alts are in radians rather than degrees.
    return maxAlt > math.degrees(body.alt) > minAlt
               

def convert_dms(angle):
    # Convert from PyEphem's ASCII-friendly degrees:minutes:seconds 
    # format to a more stylish UTF-8 string.  
    d,m,s = ("%s"%angle).split(':')
    return u"%s°%s'%s\""%(d,m,s)
                                  
def align( options, targets ):
    # TODO
    # we want 3 bright stars with moderate elevations (30-60 degrees) 
    # that are far apart in the sky and are not colinear.
    pass
                 
def get_ephem_time(t):
    # This is a horrible hack to convert Unix epoch time (seconds since midnight 1/1/1970)
    # to ephem time (days since noon 12/31/1899).
    K_EPHEM = 42160.34627314815
    K_UNIX = 1433621918.381372
    
    return date( ((t - K_UNIX) / 86400.0) + K_EPHEM )

def make_observer( options, t ):
    # Use the specified options and PyEphem time to create an observer
    if options.city is None:
        # No city specified; use longitude/latitude/altitude.
        o = Observer()
        o.lon = options.lon
        o.lat = options.lat
        o.elevation = options.elevation
    else:
        o = city(options.city)
        
    o.date = t
    return o
            

def eyepiece_for_size( size ):
    # Given an angular size in seconds of arc, return a string describing a 
    # suitable eyepiece to use for the viewing.
    
    # For stars and other bodies with effectively zero angular size, any eyepiece 
    # size is suitable and you'll use a wide FOV (to ease target-finding and reduce 
    # jitter) with good optical quality; otherwise you would want one that 
    # properly encompasses the target.
                    
    if size < 1:
        return " "
        
    # The FOV to focal length ratio is different for different eyepieces, 
    # so YMMV, but my 9mm has about 42 arcminute FOV. 
    
    # TODO -- let the user specify a set of valid eyepiece sizes, since 
    # these vary widely.
    mm = int(size * 0.004) 
    if mm < 3:
        mm = 3   
    
    return "%dmm"%mm  

# We want to sort the viewing target list in generally West-to-East order, 
# but with a goal of reducing the total path length, like a traveling 
# salesman problem. A strict W-E order could require the viewer to zigzag 
# North-and-South a lot. 

# Since the naive approach to the traveling salesman problem is factorial
# time, we will do an initial ordering West to East, then recursively 
# subdivide the problem into sets small enough to handle quickly. This 
# helps maintain the W-E order as well as speeding up the algorithm.

# Strangely, on a big set, I get an immediate solution for limit 11 (a 
# small fraction of a second), but limit 12 takes longer than I care to wait;
# Traveling salesman should be factorial time, so limit 12 should take only ~12 
# times as long as limit 11. Since I don't understand the dramatic difference
# (cache blown?), I'll leave this at a conservative 10. 
OPTIMIZATION_SUBDIVIDE_LIMIT = 10

def path_length( candidate ): 
    # Here, candidate is a list of ((x,y),description,body) tuples.
    
    # Path length accumulator.
    d = 0 
    
    # Find the path length, using the x-y coordinate system we used for 
    # W-E ordering.
    for i,rec in enumerate(candidate[:-1]):
        # This element.
        ((x0,y0),d0,b0) = rec
        # Next element.
        ((x1,y1),d1,b1) = candidate[i+1]
        # Pythagorean distance between.
        d += math.hypot( x1-x0, y1-y0 )
        
    return d
        
def optimize_order( located ): 
    # Here, located is a list of ((x,y),description,body) tuples.
    # On top-level call it's the full list of targets; on
    # recursive calls it will be a copy of a slice of the list.

    # Sort west-to-east to start; western targets will be first 
    # lost below the horizon.
    located.sort( key=lambda ((x,y),d,b): x )
    
    # If the list is long, split it into two smaller lists 
    # and optimize each one separately.
    count = len(located)
    if count > OPTIMIZATION_SUBDIVIDE_LIMIT:
        # Split the list. Put the pivot into
        # both sublists, so the first one doesn't 
        # end far from where the second one starts.
        half = count//2
        a = located[:half+1]
        b = located[half:] 
        # But take the duplicate out when building the combined list.        
        return optimize_order(a[:-1]) + optimize_order(b)
             
    # This list or sublist is small enough to exhaustively 
    # optimize. Keep the endpoints unchanged, but consider
    # all the intermediate pathing options.    
    
    # Find the best candidate
    best_candidate = None
    best_length = 1e10
    # The middle part of the list is what we vary.
    middle = located[1:-1]   
    # Iterate over all possible permutations
    for perm in itertools.permutations( middle ):
        # Build a candidate ordering from the permutation.
        candidate = [located[0]] + list(perm) + [located[-1]]
        # Find the path length.
        l = path_length( candidate )
        # Is it best so far?
        if l < best_length:
            best_length = l
            best_candidate = candidate

    return best_candidate

def present_plan( options, targets ):
    # Present the viewing plan.
    
    # Place the observer in space and time                     
    observer = make_observer( options, options.start_time )      
     
    # Restrict the targets to those within the specified altitudes
    located = []
    for desc,body in targets:
        body.compute(observer)
        if body_in_altitude_range(body,options.minalt,options.maxalt):            
            # Convert coordinates. 
            # Treat alt-azimuth as polar coordinates, with the alt angle (decreasing) 
            # as the radius (increasing). 
            # Convert that polar coordinate to rectangular.
            r = 90.0-math.degrees(body.alt)
            # Azimuth is radians east of north, that is, clockwise from 12:00. 
            # Thus y is positive north, x positive east.
            y = math.cos( body.az ) * r
            x = math.sin( body.az ) * r
            located.append( ((x,y),desc,body) ) 
    
    if len(located) > 1:
        located = optimize_order( located ) 
    
    # Now redo each body over the time span of the viewing session.
    count = len(located)

    if count > 0:
             
       if options.end_time > options.start_time:
           session_length = options.end_time-options.start_time
           interval = session_length / count
       else:
           # If end time wasn't given, allow 5 minutes per target.
           interval = (5.0/1440.0)
    
    # When converting from localtime to GMT and back in the Pyephem date 
    # format, we can incur a rounding error which makes a 9pm start time
    # show as 8:59 in the plan. We add in a little fudge factor here and
    # present only hours and minutes in the plan to keep things looking 
    # good.
       t = date(options.start_time  + 0.0002)
                                 
       print u"%5s  %20s  %13s  %13s  %5s  %6s  %20s "%("Time", "Name","Azimuth","Altitude","Mag","Eyepc","Description") 
       print u"%5s  %20s  %13s  %13s  %5s  %6s  %20s "%("-"*5,"-"*20,"-"*13,"-"*13,"-"*5,"-"*6,"-"*20) 

       for (x,y),desc,body in located:
           observer.date = t
           body.compute(observer)
           commonName = body.name.split('|')[0]
        
           if "star" in desc:
               eyepiece = " "
           else:        
               eyepiece = eyepiece_for_size(body.size)        
         
           azi = convert_dms(body.az)
           alt = convert_dms(body.alt) 
        
           m = re.search( r"(\d\d:\d\d:\d\d)", "%s"%(localtime(t)) )
           time_rep = m.group(0)[:-3]
           print u"%5s %20s  %13s  %13s  %5.1f  %6s  %20s"%(time_rep,commonName,azi,alt,body.mag,eyepiece,desc)
        
           t = date(t+interval)

    else:
        print " No objects found."
                       
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Specify the location being observed from. Defaults to my backyard in Oakland; you can 
    # specify either one of PyEphem's known cities, or a latitude/longitude.
    parser.add_argument( '--city', help="city to observe from", default=None )
    parser.add_argument( '--lat', help="latitude to observe from (degrees:minutes:seconds)", default="37:50:15.3" )
    parser.add_argument( '--lon', help="longitude to observe from (degrees:minutes:seconds, positive East) ", default="-122:16:51.6"  )
    parser.add_argument( '--elevation', help="elevation to observe from (m)", default=14 )
    # Specify a time window for the viewing plan, using natural language relative time specifications
    parser.add_argument( '--start', help="time to start the plan", default="in 1 hour" )
    parser.add_argument( '--end', help="time to end the plan", default="in 2 hours" )
    # Control categories of viewing targets.
    parser.add_argument( '--stars', help="include interesting stars in plan", action='store_true',default=False )
    parser.add_argument( '--planets', help="include planets and the moon in plan", action='store_true',default=False )
    parser.add_argument( '--messier', help="include nebulae and other DSOs from the Messier catalogue in plan", action='store_true',default=False )
    parser.add_argument( '--ngc', help="include nebulae and other DSOs from the NGC catalogue in plan", action='store_true',default=False )
    # Avoid listing many very dim targets. 
    parser.add_argument( '--starlimit', help="magnitude limit for stars", type=float,default=2.5 )
    parser.add_argument( '--dsolimit', help="magnitude limit for DSOs", type=float,default=5 )                  
    # Limit minimum and maximum elevation altitudes. Viewing sites with surrounding trees or walls 
    # restrict the minimum practical elevation, while scope mounts may limit the maximum elevation. 
    parser.add_argument( '--minalt', help="minimum observation altitude (degrees elevation)", default=20 )
    parser.add_argument( '--maxalt', help="maximum observation altitude (degrees elevation)", default=70 )
    
    # TODO add an RA/dec display option
        
    options = parser.parse_args( sys.argv[1:] )  
    
    if not (options.stars or options.planets or options.messier or options.ngc):
        options.planets = True
        options.messier = True 
        options.ngc     = True       

    cal = parsedatetime.Calendar()
    
    start_st,_ = cal.parse(options.start)
    options.start_time = get_ephem_time( time.mktime(start_st) )

    end_st,kind = cal.parse(options.end)
    options.end_time = get_ephem_time( time.mktime(end_st) )
    
    if options.end_time < options.start_time:
        # if not present or not valid, make the end time the same as the start time; we'll 
        # make it sane later. 
        options.end_time = options.start_time
        
    print "Your viewing plan:"
    #print " viewing from %s until %s (UTC)"%(options.start_time,options.end_time)
    print " viewing from %s (UTC)"%(options.start_time)
    if options.city is not None:        
        print " viewing from %s"%(options.city)
    else:
        print " viewing from latitude %s, longitude %s"%(convert_dms(options.lat),convert_dms(options.lon))
    if options.planets:
        print " including planets"
    if options.stars:
        print " including interesting stars down to magnitude %.1f"%(options.starlimit)   
    if options.messier:
        print " including nebulae and other DSOs from the Messier catalogue down to magnitude %.1f"%(options.dsolimit)   
    if options.ngc:
        print " including nebulae and other DSOs from the NGC catalogue down to magnitude %.1f"%(options.dsolimit)

   
    print " limiting targets to altitudes between %d and %d degrees elevation"%(options.minalt,options.maxalt)
    
    print
             
    # Start assembling our target list.
    targets = []
    # Filter the targets by magnitude using the initial time; assume magnitude
    # won't change dramatically over the course of a single night. 
    observer = make_observer( options, options.start_time )  
    # Did we request stars?
    if options.stars:
        # Iterate over the star list
        for desc,body in star_candidates():
            body.compute(observer) 
            # Keep the stars below the magnitude limit            
            if body.mag <= options.starlimit:
                targets.append( (desc,body) )
    # Did we request DSOs from the Messier catalogue?
    if options.messier:
        # Iterate over the Messier DSO list
        for desc,body in messier_candidates():
            body.compute(observer)             
            # Keep the DSOs below the magnitude limit            
            if body.mag <= options.dsolimit: 
                targets.append( (desc,body) ) 
    # Did we request DSOs from the Messier catalogue?
    if options.ngc:
        # Iterate over the NGC DSO list
        for desc,body in ngc_candidates():
            body.compute(observer)
            # Keep the DSOs below the magnitude limit
            if body.mag <= options.dsolimit:
                targets.append( (desc,body) )
                 
    # Did we request planets?
    if options.planets:
        # Assume all planets are bright and interesting
        targets.extend( planet_candidates() ) 
  
    present_plan(options,targets)
