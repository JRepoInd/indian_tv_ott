import xbmc, xbmcgui, xbmcplugin
import urlparse
import xbmcaddon
import time
from operator import itemgetter

from F4mProxy import f4mProxyHelper
import urllib2
import urllib
import json
import traceback
import os

__addon__       = xbmcaddon.Addon()
__addonname__   = __addon__.getAddonInfo('name')
__icon__        = __addon__.getAddonInfo('icon')
addon_id = 'plugin.video.indianott'
selfAddon = xbmcaddon.Addon(id=addon_id)
__addonpath__ = selfAddon.getAddonInfo('path')

def fetch_url(url, data=None):
	if data:
		data = urllib.urlencode(data)
	req = urllib2.Request(url, data)
	req.add_header('User-Agent', 'Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10')

	req.add_header('Referer', 'http://www.yupptv.in/')

	return json.load(urllib2.urlopen(req))

def get_languages():
	with open(os.path.join( __addonpath__, 'resources','data','languages.json')) as f:
		return json.load(f)

def get_channel_list(lang='HIN', vtenantId=3):
	result = fetch_url('http://apidon.yupptv.in/YuppSlateMobileService.svc/getlivetv/v2?vdevid=5&vlngid=%s&vtenantId=%s&format=json'%(lang, vtenantId))
	
	if 'ChannelItem' in result:
		return result['ChannelItem']
		# for channel in data['ChannelItem']:
		# 	print channel['ID'], channel['ChannelCode'], channel['Description'], channel['PayType'], channel['Imgpath'], channel['pcimageurl']

def get_channel_stream_by_name(ChannelCode):
	if not name:
		return
	data = {
			"vdevid":5,
			"vtenantId":3,
			"vstreamname":ChannelCode,
			"vstreamkey":"LIVE",
			"vapi":"",
			"vuserid":"",
			"vbox":"",
			"format":"json",
			"isseekstarttime":"",
			"isseekendtime":"",
		}
	result = fetch_url('http://apidon.yupptv.in/YuppSlateMobileService.svc/getstreamurlbyname', data)
	print result
	streamurl = result["streamurl"]+"&hdcore=3.8.0"
	return streamurl


def PlayLiveLink ( name="9XM" ): 
	url=get_channel_stream_by_name(name)

	player=f4mProxyHelper()
	player.playF4mLink(url, name)


def addLink(name,mode,iconimage):
	ok=True
	rname=  name.encode("utf-8")
	u=sys.argv[0]+"?mode="+str(mode)+"&name="+urllib.quote_plus(rname)

	liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
	return ok

def addDir(name,code,mode,iconimage,showContext=False,isItFolder=True):
	rname=  name.encode("utf-8")
	
	print rname
	print iconimage
	u=sys.argv[0]+"?mode="+str(mode)+"&name="+urllib.quote_plus(code)

	ok=True
	liz=xbmcgui.ListItem(rname, iconImage="DefaultFolder.png", thumbnailImage=iconimage)

	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=isItFolder)
	return ok
	
def AddLanguages():
	for lang in get_languages():
		addDir(lang['LangName'],lang['LangId'], 2, iconimage="DefaultFolder.png")


def AddChannels(lang):
	for channel in get_channel_list(lang):
		# url = get_channel_stream_by_name(channel['ChannelCode'])
		# print url
		addLink(channel['Description'], mode=3, iconimage=channel['Imgpath'])

def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]
				
	return param

#print "i am here"
params=get_params()
url=None
name=None
mode=None


try:
	url=urllib.unquote_plus(params["url"])
except:
	pass
try:
	name=urllib.unquote_plus(params["name"])
except:
	pass
try:
	mode=int(params["mode"])
except:
	pass
	

print mode,name

try:
				
	if mode==None:
		print "In Parent Folder"
		AddLanguages()
	elif mode==2:
		print "Ent name is "+name
		AddChannels(name)

	elif mode==3:
		print "Ent name is "+name
		PlayLiveLink(name)


except:
	print 'somethingwrong'
	traceback.print_exc(file=sys.stdout)

# try:
# 	if (not mode==None) and mode>1:
# 		view_mode_id = get_view_mode_id('thumbnail')
# 		if view_mode_id is not None:
# 			print 'view_mode_id',view_mode_id
# 			xbmc.executebuiltin('Container.SetViewMode(%d)' % view_mode_id)
# except: pass

if not ( mode==3 ):
	xbmcplugin.endOfDirectory(int(sys.argv[1]))