import httplib
from pyamf import AMF0, AMF3

from pyamf import remoting
from pyamf.remoting.client import RemotingService

playerKey = "AQ~~,AAAA0Zd2KCE~,a1ZzPs5ODGffVvk2dn1CRCof3Ru_I9gE"
#playerKey = "AAAAAGLvCOI~,a0C3h1Jh3aQKs2UcRZrrxyrjE0VH93xl"

def build_amf_request(const, playerID, videoPlayer, publisherID):
    env = remoting.Envelope(amfVersion=3)
    env.bodies.append(
        (
            "/3",
            remoting.Request(
                target="com.brightcove.player.runtime.PlayerMediaFacade.findPagingMediaCollectionByReferenceId",
                body=[const, playerID, videoPlayer,0,50, publisherID],
				#body=["8e99dff8de8d8e378ac3f68ed404dd4869a4c007",1254928709001,"1259322203560",0,50,900189268001],
                #body=["8e99dff8de8d8e378ac3f68ed404dd4869a4c007", 1254928709001, 1259322203560, 900189268001],
                envelope=env
            )
        )
    )
    return env

def get_clip_info(const, playerID, videoPlayer, publisherID):

    conn = httplib.HTTPConnection("c.brightcove.com")
    envelope = build_amf_request(const, playerID, videoPlayer, publisherID)
    conn.request("POST", "/services/messagebroker/amf?playerKey=" + playerKey, str(remoting.encode(envelope).read()), {'content-type': 'application/x-amf'})
    response = conn.getresponse().read()
    response = remoting.decode(response).bodies[0][1].body
    return response

def play(const, playerID, videoPlayer, publisherID, height):
    rtmpdata = get_clip_info(const, playerID, videoPlayer, publisherID)
    rtmpdata = rtmpdata["videoDTOs"][0]

    streamName = ""
    streamUrl = "";
    
    for item in sorted(rtmpdata['renditions'], key=lambda item:item['frameHeight'], reverse=False):
        streamHeight = item['frameHeight']
        
        if streamHeight <= height:
            streamUrl = item['defaultURL']
    
    streamName = streamName + rtmpdata['displayName']
    return [streamName, streamUrl];
	
