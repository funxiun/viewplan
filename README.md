## Viewplan

Viewplan is a Python3 script for generating telescope viewing plans for amateur astronomers. 

You specify the time and location for the viewing, and what sort of objects you're interested in; the program selects a list of viewable objects for the specified time and location, and generates a viewing plan with azimuth, altitude, and other information for each target. 

The output is sorted generally from West to East (with some path length optimization) so by visiting the targets in the presented order you can generally catch them before they set.

### Dependencies

Viewplan requires the following third party Python packages:

* [PyEphem](http://rhodesmill.org/pyephem/) - This does the heavy astronomical lifting.
* [parsedatetime](https://github.com/bear/parsedatetime) - This provides the handy natural language time parsing on the command line. 
* [urllib3](https://github.com/urllib3/urllib3) - Python HTTP library.

Works on my machine with Python 3.5.3. 

### Examples

You're near Utrecht, The Netherlands, you want to start watching right away, light pollution is making 
it impossible to see faint nebulae, but you wouldn't mind seeing some bright double 
stars.  

~~~
: python viewplan.py --city Utrecht --planets --messier --ngc --dsolimit 5.5 --stars --starlimit 1.8 --start 03:00 

Your viewing plan:
 viewing from 2018/4/12 01:00:00 (UTC)
 viewing from Utrecht
 including planets
 including interesting stars down to magnitude 1.8
 including nebulae and other DSOs from the Messier catalogue down to magnitude 5.5
 including nebulae and other DSOs from the NGC catalogue down to magnitude 5.5
 limiting targets to altitudes between 20 and 70 degrees elevation

                Name        Azimuth       Altitude    Mag   Eyepc           Description 
--------------------  -------------  -------------  -----  ------  -------------------- 
            Regulus   259°51'21.1"    22°49'28.2"    1.4            visual double star
            NGC 771    11°51'36.6"    36°44'54.9"    4.0                          star
           NGC 4530   292°08'25.9"    36°58'48.0"    4.3                          star
           Arcturus   273°16'12.9"    21°57'23.6"    0.2                 variable star
              Spica   283°19'02.1"   -24°15'50.3"    1.1            visual double star
            Jupiter   276°16'28.8"   -26°24'22.5"   -2.3     3mm                planet
               Vega   293°29'36.2"    32°06'24.3"    0.0            visual double star
              Deneb   295°24'19.6"    40°18'51.5"    1.3            visual double star
                M39   304°49'44.0"    36°11'06.4"    4.6     7mm          open cluster
           NGC 7000   320°33'16.7"    18°42'18.3"    4.0    28mm         bright nebula
           NGC 6871   343°41'17.3"     0°12'11.8"    5.2     7mm          open cluster
           NGC 6633    31°57'56.8"   -26°33'19.7"    4.6     4mm          open cluster

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
                   [--comets]
                   [--planetoids]
                   [--starlimit STARLIMIT]
                   [--dsolimit DSOLIMIT] 
                   [--minalt MINALT]
                   [--maxalt MAXALT]
~~~
                        
##### Location Options
The viewing location can be provided either with a city name such as `--city Utrecht` or a latitude/longitude/elevation coordinate set ("ICBM coordinates") such as `--lat 52:5:26.9 --lon 5:7:10.76 --elevation 13`.

The city name must be one of the (relatively few) cities in the PyEphem database. Latitude and longitude are given in "degrees:minutes:seconds" format (positive longitude east), and elevation in meters above sea level.  

If neither city nor coordinates are given, the script assumes you're viewing from my hometown Utrecht, The Netherlands.

##### Time Options

The viewing start time can be given in natural and relative language, e.g. `--start 9pm` or `--start "in 2 hours"` or `--start "tuesday 11pm"` (the quotation marks are required if there are spaces in the time description). Local time is assumed. 

##### Filter Options

You can request that planets, comets, planetoids, "interesting" stars, and other deep space objects (DSOs) such as galaxies, nebulae and clusters be listed, using the `--planets`, `--comets`, `--planetoids`, `--stars`, `--messier` and `--ngc` options. If none of those six options are provided, planets and DSOs from the Messier catalogue will be listed. 

By default, stars below magnitude 2.5 and DSOs below magnitude 5 are filtered out. The limiting magnitudes can be set, for instance including dimmer stars with `--starlimit 3.5` or keeping only the brightest DSOs with `--dsolimit 4.5`. 

Only targets whose altitude (elevation angle) are within a set range will be shown. This is handy if your local horizon is obscured by walls, trees, etc., or if your telescope mount isn't capable of elevating all the way to zenith. `--minalt 10` sets a floor 10 degrees above the horizon; `--maxalt 80` sets an upper limit of 80 degrees above the horizon. The defaults are 20 and 70 degrees. 

### Future Work

* Add other Deep Sky catalogues (Melotte, Caldwell, Abell etc.)
* Moon phase (percentage luminated). Also rise, transit & set to be shown.
* Display Civil, Nautical & Astromomical twilight
* Introduce a configfile with default settings (the commandline can get a bit long :)
* ISS overpass alert
* Show only results from a specified azimuth range
* CSV, EQ Tour output

From the original repository https://github.com/borogove/viewplan:

* Add an option to display RA and declination instead of altitude and azimuth.
* Add an option to display good candidate stars for alignment.
* Allow the user to specify what eyepiece focal lengths they have available.
* Add an end time option, allowing targets to be considered which are below the eastern horizon at the start of the plan.


