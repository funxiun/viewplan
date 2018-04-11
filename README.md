## Viewplan

Viewplan is a Python script for generating telescope viewing plans for amateur astronomers. 

You specify the time and location for the viewing, and what sort of objects you're interested in; the program selects a list of viewable objects for the specified time and location, and generates a viewing plan with azimuth, altitude, and other information for each target. 

The output is sorted generally from West to East (with some path length optimization) so by visiting the targets in the presented order you can generally catch them before they set.

### Dependencies

Viewplan requires the following third party Python packages:

* [PyEphem](http://rhodesmill.org/pyephem/) - This does the heavy astronomical lifting.
* [parsedatetime](https://github.com/bear/parsedatetime) - This provides the handy natural language time parsing on the command line.    

Works on my machine with Python 2.7. 

### Examples

You're near Boston, you want to start watching right away, light pollution is making 
it impossible to see faint nebulae, but you wouldn't mind seeing some bright double 
stars.  

~~~
: python viewplan.py --city Boston --start "in 15 minutes" 
        --planets --messier --dsolimit 4 --stars --starlimit 1.8

Your viewing plan:
 viewing from 2015/6/7 05:45:26 (UTC)
 viewing from Boston
 including planets
 including interesting stars down to magnitude 1.8
 including nebulae and other DSOs from the Messier catalogue down to magnitude 4.0
 limiting targets to altitudes between 20 and 70 degrees elevation

                Name        Azimuth       Altitude    Mag   Eyepc           Description 
--------------------  -------------  -------------  -----  ------  -------------------- 
              Alioth   313°55'37.3"    40°40'24.4"    1.8            visual double star
            Arcturus   262°05'47.8"    37°18'15.2"    0.2                 variable star
              Altair   136°30'00.5"    48°52'58.3"    0.9            visual double star
               Deneb    70°13'08.0"    61°23'05.9"    1.3            visual double star
    Andromeda Galaxy    51°55'55.5"    20°17'24.0"    3.5    45mm         spiral galaxy
              Saturn   212°51'44.0"    22°49'14.9"    0.1     3mm                planet
                Moon   132°09'15.4"    20°19'51.2"  -12.4     7mm                  moon
~~~ 

### Options

~~~
usage: viewplan.py [-h] 
                   [--city CITY]
                   [--lat LAT]
                   [--lon LON]
                   [--elevation ELEVATION]
                   [--start START]
                   [--stars]
                   [--planets]
                   [--messier]
                   [--ngc]
                   [--starlimit STARLIMIT]
                   [--dsolimit DSOLIMIT] 
                   [--minalt MINALT]
                   [--maxalt MAXALT]
~~~
                        
##### Location Options
The viewing location can be provided either with a city name such as `--city Boston` or a latitude/longitude/elevation coordinate set ("ICBM coordinates") such as `--lat 33:27:00 --lon -112:04:00 --elevation 331`.

The city name must be one of the (relatively few) cities in the PyEphem database. Latitude and longitude are given in "degrees:minutes:seconds" format (positive longitude east), and elevation in meters above sea level.  

If neither city nor coordinates are given, the script assumes you're viewing from my backyard in Oakland, CA.

##### Time Options

The viewing start time can be given in natural and relative language, e.g. `--start 9pm` or `--start "in 2 hours"` or `--start "tuesday 11pm"` (the quotation marks are required if there are spaces in the time description). Local time is assumed. 

##### Filter Options

You can request that planets, "interesting" stars, and other deep space objects (DSOs) such as galaxies, nebulae and clusters be listed, using the `--planets`, `--stars`, `--messier` and `--ngc` options. If none of those four options are provided, planets and DSOs from the Messier and NGC catalogue will be listed. 

By default, stars below magnitude 2.5 and DSOs below magnitude 5 are filtered out. The limiting magnitudes can be set, for instance including dimmer stars with `--starlimit 3.5` or keeping only the brightest DSOs with `--dsolimit 4.5`. 

Only targets whose altitude (elevation angle) are within a set range will be shown. This is handy if your local horizon is obscured by walls, trees, etc., or if your telescope mount isn't capable of elevating all the way to zenith. `--minalt 10` sets a floor 10 degrees above the horizon; `--maxalt 80` sets an upper limit of 80 degrees above the horizon. The defaults are 20 and 70 degrees. 

### Future Work

* Add observable comets
* Add observable asteroids
* Add other Deep Sky catalogues (Caldwell, Abell etc.)
* Moon phase (percentage luminated)
* ISS overpass alert
* Show only results from a specified azimuth range
* Convert to Python 3.x

From the original repository https://github.com/borogove/viewplan:

* Add an option to display RA and declination instead of altitude and azimuth.
* Add an option to display good candidate stars for alignment.
* Allow the user to specify what eyepiece focal lengths they have available.
* Add an end time option, allowing targets to be considered which are below the eastern horizon at the start of the plan.


