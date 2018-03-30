IDEAs
=====

- Autoplay or autogenerate playlist from import
  Needs app suport (see below)

- Upload stuff to somewhere
  Needs app suport (see below)


TODO
====
- Merge Command, AppletCommandMixin, APIEndpoint, AppletAPIEndpointMixin and Applet
- The falcon router is the analogous case for ArgumentParser, should be passed to the merged Applet to autoconfigure children stuff
- Remove argument and use Paramter


App Bridges
===========

Special classes that allow intercomunication with some apps

Examples:

* Banshee bridge:
  - Can list contents for some playlists/artists/albums
  - Can play some stuff (MPRIS bridge?)

* Shotwell bridge:
  - List tags, searches, events, etc...


Hierachy
========
- Extension
  +- Command
  +- 

- HKExtension

- Applet
