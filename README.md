# COH1 Python Replay Parser
 A replay parser for company of heroes one. 

So far parses the following information from replays.

Version v301.44802 - Relic Chunky Version 3.

*fileVersion         # 8 for Version v301.44802
*chunkyVersion       # 3 for Version v301.44802
*randomStart         # True/False
*highResources       # True/False
*VPCount             # multiple of 250 VPs
*matchType           # eg automatch
*localDate           # the date is specific to the OS the game was recorded on.
*replayName          # the game name or None if from TEMP/memory
*gameVersion         # 301.44802 [02/21/17 10:12:54]
*modName             # RelicCOH # RelicCoHO
*mapName             # ucs link to full map name in ucs locale file.
*mapNameFull         # full name taken from ucs file.
*mapDescription      # ucs link to full map description.
*mapDescriptionFull  # full description taken from ucs file.
*mapFileName         # location of the map file 
*mapWidth            # number of tiles
*mapHeight           # number of tiles
*playerList          # [(steamName, factionName)]
