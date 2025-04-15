# follow this to install pygobject: https://pygobject.gnome.org/getting_started.html
import asyncio
from typing import Any, Callable
from dbus_next import Message
from dbus_next.aio import MessageBus
import math
from main import DataProtocol
from main import LimitedTransport
import time

# {"player": player, "properties": properties, "base": base, "metadata": metadata, "trackTitle": trackTitle, "trackArtist": trackArtist}
class MediaSource:
    def __init__(self, player=None, properties=None, base=None, metadata=None, trackTitle="", trackArtist="", length=1, volume=-1):
        self.player = player
        self.properties = properties
        self.base = base
        self.metadata = metadata
        self.trackTitle = trackTitle
        self.trackArtist = trackArtist
        self.length = length
        self.volume = volume
        pass

    pass

class MediaPlayerVariables:
    defaultBrightness = 12
    darkMode = 4
    currentBrightness = defaultBrightness
    _foundSources: dict[str, MediaSource] = {} # Stores all the sources that exist
    _currentSource = "" # The current source name
    transport: LimitedTransport = None # The provided Serial transport for the button box
    id: int = -1 # Provided module ID by the program
    lifetime: asyncio.Task = None
    bus: MessageBus = None
    shouldRedraw: bool = True
    introspection = None
    lastInteracted = 0

    @classmethod
    def GetSource(c, name) -> MediaSource: # Gets the source by the given name, otherwise returns None
        return c._foundSources[name] if name in c._foundSources else None

    @classmethod
    def GetCurrentSource(c) -> MediaSource: # Gets the currently displayed source
        if(c._currentSource in c._foundSources):
            return c._foundSources[c._currentSource]
        return None
    
    @classmethod
    def AdjustSourceSelection(c, increment): # Changed the currently selected source by the given increment
        keys = list(MediaPlayerVariables._foundSources.keys())
        if len(keys) == 0:
            return
        curr = 0 if MediaPlayerVariables._currentSource not in keys else keys.index(MediaPlayerVariables._currentSource)
        MediaPlayerVariables._currentSource = keys[(curr+increment)%len(keys)]
    
    @classmethod
    def selectFirstSource(c): # Selects the first possible source from found sources, basically resetting the selection
        for key in c._foundSources:
            c._currentSource = key

async def get_media_players(bus: MessageBus):
    mediaplayers = []
    reply = await bus.call(Message('org.freedesktop.DBus', '/org/freedesktop/DBus', 'org.freedesktop.DBus', 'ListNames'))
    for name in reply.body[0]:
        if 'org.mpris.MediaPlayer2' in name:
            mediaplayers.append(name)
    return mediaplayers

async def UpdateScreen(transport: DataProtocol):
    try:
        source = MediaPlayerVariables.GetCurrentSource()
        if source != None:
            full = MediaPlayerVariables.shouldRedraw
            if full:
                if MediaPlayerVariables.currentBrightness != MediaPlayerVariables.defaultBrightness:
                    colorData: list[bytes] = []
                    for i in range(0, 6):
                        colorData.append(bytes([3,i,MediaPlayerVariables.defaultBrightness]))
                    transport.write(b''.join(colorData))
                MediaPlayerVariables.currentBrightness = MediaPlayerVariables.defaultBrightness
            elif time.time() - MediaPlayerVariables.lastInteracted > 10:
                if MediaPlayerVariables.currentBrightness != MediaPlayerVariables.darkMode:
                    MediaPlayerVariables.currentBrightness = MediaPlayerVariables.darkMode
                    colorData: list[bytes] = []
                    for i in range(0, 6):
                        colorData.append(bytes([3,i,MediaPlayerVariables.currentBrightness]))
                    transport.write(b''.join(colorData))
                    full = True

            # Properties for drawing
            trackLengthInSeconds = source.length/1000000
            trackPositionInSeconds = await source.player.get_position()/1000000
            trackString = f"{math.floor(trackPositionInSeconds/60)}:{str(math.floor(trackPositionInSeconds%60)).zfill(2)} / {math.floor(trackLengthInSeconds/60)}:{str(math.floor(trackLengthInSeconds%60)).zfill(2)}"
            programTitle = await source.base.get_identity()
            status = await source.player.get_playback_status()
            volume = source.volume
            artistLine = ". ".join(source.trackArtist) if isinstance(source.trackArtist, list) else source.trackArtist


            fulldata: list[bytes] = [
                b"\x04\xAF"+bytes([MediaPlayerVariables.currentBrightness, 16, 64, 0, 128, 0])+trackString.encode()+b"\n", # Current track progress text
                b"\x04\xAE"+bytes([MediaPlayerVariables.currentBrightness, 0, 64, 40, 128, 0])+status.encode()+b"\n", # Playing, paused status
                b"\x06\xA9"+bytes([0, 0, int(128*(trackPositionInSeconds/(trackLengthInSeconds if trackLengthInSeconds > 0 else 1)))+1, 16, MediaPlayerVariables.currentBrightness, MediaPlayerVariables.currentBrightness, 1]), # Progress bar 2
            ]
            if full:
                optionalData: list[bytes] = [
                    b"\x04\xAD"+bytes([MediaPlayerVariables.currentBrightness, 0, 64, 20, 128, 0])+programTitle.encode()+b"\n", # Program name
                    b"\x05\xAA"+bytes([MediaPlayerVariables.currentBrightness, 16, 64, 50, 128, 0, 0, 4, 10])+artistLine.encode()+b"\n", # Artists
                    b"\x05\xB9"+bytes([MediaPlayerVariables.currentBrightness, 16, 64, 60, 128, 0, 0, 4, 10])+source.trackTitle.encode()+b"\n", # Track title
                    b"\x04\xB1"+bytes([MediaPlayerVariables.currentBrightness, 0, 64, 78, 128, 128])+b"Volume: "+str( int(volume*100)/1).encode()+b"%\n" # Volume
                    b"\x06\xA8"+bytes([0, 0, 128, 16, MediaPlayerVariables.currentBrightness, 0, 1]), # Progress bar
                ]
                fulldata.extend(optionalData)

            transport.write(b''.join(fulldata))
            MediaPlayerVariables.shouldRedraw = False
        else:
            MediaPlayerVariables.shouldRedraw = True
            MediaPlayerVariables.selectFirstSource()
            pass
    except Exception as ex:
        print(ex)
        if ex.type == 'org.freedesktop.DBus.Error.ServiceUnknown':
            MediaPlayerVariables._foundSources.pop(MediaPlayerVariables._currentSource)
        pass

async def mediaPlayerLifetime(bus, introspection, transport: DataProtocol):
    # print("Checking for media players....")
    transport.write(b"\x00\x1F")
    transport.write(b"\x02\x00<\n")
    transport.write(b"\x02\x03>\n")    
    transport.write(b"\x02\x02|<\n")
    transport.write(b"\x02\x05>|\n")
    await generatePlayers(bus, introspection)
    MediaPlayerVariables.selectFirstSource()
    MediaPlayerVariables.shouldRedraw = True
    await UpdateScreen(transport)
    while True:
        # await generatePlayers(bus, introspection, propertyChangedCallback)
        await UpdateScreen(transport)
        await asyncio.sleep(1)

async def generatePlayers(bus, introspection):
    players = await get_media_players(bus)
    for playerName in players:
        await generatePlayer(bus, playerName, introspection)

async def generatePlayer(bus: MessageBus, playerName, introspection):
    if playerName in MediaPlayerVariables._foundSources:
        return
    obj = bus.get_proxy_object(playerName, '/org/mpris/MediaPlayer2', introspection)
    player = obj.get_interface('org.mpris.MediaPlayer2.Player')
    properties = obj.get_interface('org.freedesktop.DBus.Properties')
    base = obj.get_interface('org.mpris.MediaPlayer2')
    def _propertyChangedCallback(interface_name, changed_properties, invalidated_properties):
        # for changed, variant in changed_properties.items():
        #         print(f'[{id}] property changed: {changed} - {variant.value}')
        #         print(transport)
        if "Metadata" in changed_properties:
            source = MediaPlayerVariables.GetSource(playerName)
            if(source != None):
                print("Metadata has changed, new track?")
                if 'mpris:length' in changed_properties['Metadata'].value:
                    source.length = changed_properties['Metadata'].value['mpris:length'].value
                    print("Track length: " + str(source.length/1000000) + "s")
                if "xesam:title" in changed_properties["Metadata"].value:
                    source.trackTitle = changed_properties["Metadata"].value["xesam:title"].value
                    print("Track title: " + source.trackTitle)
                if "xesam:artist" in changed_properties["Metadata"].value:
                    source.trackArtist = changed_properties["Metadata"].value["xesam:artist"].value
                    print("Track artist: " + str(source.trackArtist))
                if source == MediaPlayerVariables.GetCurrentSource():
                    print("source is same as displayed, redrawing.")
                    MediaPlayerVariables.shouldRedraw = True
                print("")
        pass

    def _seekedCallback(position):
        loop = asyncio.get_running_loop()
        task = loop.create_task(UpdateScreen(MediaPlayerVariables.transport))
        # print(position/1000000)

    properties.on_properties_changed(_propertyChangedCallback)
    player.on_seeked(_seekedCallback)
    metadata = await player.get_metadata()
    trackTitle = "N/A"
    trackArtist = "N/A"
    if 'xesam:title' in metadata:
        trackTitle = metadata['xesam:title'].value
    if 'xesam:artist' in metadata:
        trackArtist = metadata['xesam:artist'].value
    # print(metadata['mpris:length'].value/1000000)
    try:
        volume = await player.get_volume()
    except:
        volume = -1
    trackLength = 999999999
    try:
        trackLength = metadata['mpris:length'].value
    except:
        print("couldn't get track length")
    MediaPlayerVariables._foundSources[playerName] = MediaSource(
        player=player, properties=properties, 
        base=base, metadata=metadata, 
        trackTitle=trackTitle, trackArtist=trackArtist, length=trackLength,
        volume=volume)


def clamp(n, min, max): 
    if n < min: 
        return min
    elif n > max: 
        return max
    else: 
        return n 

async def ChangeVolume(change):
    source = MediaPlayerVariables.GetCurrentSource()
    if source == None:
        return
    if source.volume >= 0:
        source.volume = clamp(source.volume + (change/100), 0, 1)
        await source.player.set_volume(source.volume)
    
    # volume = await source.player.get_volume()
    MediaPlayerVariables.transport.write(b"\x04\xB1"+bytes([MediaPlayerVariables.currentBrightness, 0, 64, 78, 128, 128])+b"Volume: "+str( int(source.volume*100)/1).encode()+b"%\n")

def Previous():
    current = MediaPlayerVariables.GetCurrentSource()
    if current != None:
        asyncio.create_task(current.player.call_previous())
    pass

def Next():
    current = MediaPlayerVariables.GetCurrentSource()
    if current != None:
        asyncio.create_task(current.player.call_next())
    pass

def PlayPause():
    current = MediaPlayerVariables.GetCurrentSource()
    if current != None:
        asyncio.create_task(current.player.call_play_pause())
    pass

#REQUIRED FUNCTIONS

# Initialisation function
async def init(propertyChangedCallback: Callable[[Any, str], Any], transport: LimitedTransport):
    bus = await MessageBus().connect()
    MediaPlayerVariables.bus = bus
    players = await get_media_players(bus)

    with open('mpris-dbus-interface.xml', 'r') as f:
        introspection = f.read()

    MediaPlayerVariables.introspection = introspection

    loop = asyncio.get_running_loop()
    task = loop.create_task(mediaPlayerLifetime(bus, introspection, transport))

    MediaPlayerVariables.lifetime = task
    MediaPlayerVariables.transport = transport
    # try:
        # loop.run_until_complete(task)
    # except asyncio.CancelledError:
        # pass
    print("mediaplayer intialized")
    MediaPlayerVariables.id = transport.id
    return

# Input handler
def handleInput(bank, button, state, rotation):
    MediaPlayerVariables.lastInteracted = time.time()
    if button == 0 and state == 2 and (bank == 0 or bank == 1):
        modifier = -1 if bank == 0 else 1 if bank == 1 else 0
        asyncio.create_task(generatePlayers(MediaPlayerVariables.bus, MediaPlayerVariables.introspection))
        MediaPlayerVariables.AdjustSourceSelection(modifier)
        MediaPlayerVariables.shouldRedraw = True
        asyncio.create_task(UpdateScreen(MediaPlayerVariables.transport))
    if button == 2 and state == 2 and (bank == 0 or bank == 1):
        if bank == 0:
            Previous()
        else:
            Next()
    if bank == 2 and button == 0 and state == 2:
        PlayPause()
    if bank == 2 and button == 1:
        change = -rotation if state == 1 else rotation
        asyncio.create_task(ChangeVolume(change*2))
        # asyncio.create_task(MediaPlayerVariables.foundSources[MediaPlayerVariables.currentSource]["player"].call_play_pause())

    # loop = asyncio.get_running_loop()
    pass

# Redraw request function
def redraw():
    loop = asyncio.get_running_loop()
    task = loop.create_task(_redraw())
    pass

async def _redraw():
    transport = MediaPlayerVariables.transport
    transport.write(b"\x00\x1F")
    transport.write(b"\x02\x00<\n")
    transport.write(b"\x02\x03>\n")    
    transport.write(b"\x02\x02|<\n")
    transport.write(b"\x02\x05>|\n")
    MediaPlayerVariables.shouldRedraw = True
    await UpdateScreen(transport)

# Stop request
def stop():
    print("stopping")
    MediaPlayerVariables.bus.disconnect()
    MediaPlayerVariables.lifetime.cancel()
    pass