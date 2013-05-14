About
=====

This is a project I started one night to parse GPS (and acceleration data) from my data-logger into data vs position (rather than time) data.  I hope to actually document it and expand it soon.  For now, this is the only documentation there is.

For an idea of what this project does see the blog posts see these two [blog] [1] [posts] [2].

Dependencies
============
I can't remember what python packages this depends on but I think you'll need at least:

1. Python 2.7 (2.6 will probably work)
2. PyGame (for plotting the GPX file)

Usage
=====
To use this you need two things other than the source.  

1. Your GPS log with NEMA GPRMC messages (including checksum).
2. a .gpx file that traces out the track.  (can be created from bing maps)

for now the paths are all hard coded (sorry.  I'll fix it.) and you'll have to read the code to find out more (sorry again.)

Licence
=======
You can do what ever you want with this code so long as

1. You let me know by either dropping me a message (email, github, or similar), or forking on github.  This is entirely for my ego. ;)
2. I'm not responsible for anything you do and this software is provided "as is" and with out warranty bla bla*

if you can't handle the above two things then you can't use it.

*THIS SOFTWARE IS PROVIDED ``AS IS'' AND WITHOUT ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. 






[1]: http://roadtochumpcar.com/datalogger/ 
[2]: http://roadtochumpcar.com/data-lots-of-data/