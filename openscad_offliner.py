'''
-------------------------------------------------------------------------
openscad_offliner.py: Download OpenSCAD online doc for offline reading

Copyright (C) 2015 Runsun Pan (run+sun (at) gmail.com) 
Source: https://github.com/runsun/faces.scad
This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License along 
with this program; if not, see <http://www.gnu.org/licenses/gpl-2.0.html>
-------------------------------------------------------------------------

Require: python 2.7, BeautifulSoupt 4.0 above

Usage:
		1) Save this file in folder x.
		2) In folder x, type: 
			
			  python openscad_offliner.py 

		   or to save log to a file:  
	
			  python openscad_offliner.py > openscad_offliner.log

		All web pages will be saved in x/openscad_docs, 
		and all images in x/openscad_docs/imgs  

Note: 

	1) All html pages are stored in dir_docs (default: openscad_docs)
	2) All images are stored in dir_imgs (default: openscad_docs/imgs)
	3) All OpenSCAD-unrelated stuff, like wiki menu, etc, are removed
	4) All wiki warnings sign are removed
	5) Search box is hidden. There might be a way (i.e., javascript) to 
		search the doc but we leave that to the future.

git: https://github.com/runsun/openscad_offliner

'''

##
## Developer Note: handle_page() is the main function
##

import urllib, urllib2, os, time, sys
from bs4 import BeautifulSoup as bs

##
## Data url
##
url = 'https://en.wikibooks.org/wiki/OpenSCAD_User_Manual'
url_wiki = 'https://en.wikibooks.org'
url_openscadwiki = '/wiki/OpenSCAD_User_Manual'
url_offliner= 'https://github.com/runsun/openscad_offliner'

print "[Remote]"
print "url= ", url
print "url_wiki= ", url_wiki
print "url_openscadwiki= ", url_openscadwiki
print "url_offliner= ", url_offliner


##
## Set folders:
##

this_dir = os.path.dirname(os.path.abspath(__file__))
dir_docs = 'openscad_docs'                       
dir_imgs =  os.path.join( dir_docs, 'imgs')  
dir_styles =  'styles'   
dir_styles_full = os.path.join( dir_docs, 'styles') 

if not os.path.exists(dir_docs): os.makedirs(dir_docs)
if not os.path.exists(dir_imgs): os.makedirs(dir_imgs)
if not os.path.exists(dir_styles_full): os.makedirs(dir_styles_full)
print "\n[Local]"
print "this_dir= " + this_dir
print "dir_docs= " + dir_docs
print "dir_imgs= " + dir_imgs
print "dir_styles= " + dir_styles
print "dir_styles_full= " +dir_styles_full


##
## Buffer to keep track of downloaded to avoid repeating downloads
##
pages= [] # Urls of downloaded pages
imgs = [] # Local paths of downloaded images 
styles=[] # stylesheet urls


def sureUrl(url):
  ''' Return proper url that is complete and cross-platform '''
  if url.startswith('//'):
  		url = 'https:' + url
  elif not url.startswith( url_wiki ):
    #print ind + ':: url not starts with url_wiki("%s"), changing it...'%url_wiki
    url = urllib2.urlparse.urljoin( url_wiki, url[0]=="/" and url[1:] or url)    
  
  return url 
  
##========================================================
##
##   styles
##
##========================================================

'''
We use a var styles (which is a list of style urls) to keep 
track of the styles downloaded. If a style url already in styles, 
skip downloading. 

All style files will be saved as style_?.css where ? is an integer.

Two kind of styles need to be handled:

1) linked_style:

	loaded by <link href="..../load.php...">

	They are handled by download_style_from_link_tag( soup_link, ind ) 
	whenever necessary. 

2) Imported_style

	loaded by a line in a style file (that could be a linked_style):

		@import url(...) screen;

	This is handled by download_imported_style( csstext, ind )

Note: Maybe a class like: StyleReader is good for this ?
'''

def handle_styles( soup, ind ):

	for link in soup.find_all('link'):

		#href = link.get('href')
		href = sureUrl( link.get('href') )
    
		#if not href.startswith( url_wiki ):
		#  href = os.path.join( url_wiki, href)
    
		if '/load.php?' in href:
			download_style_from_link_tag( soup_link=link, ind=ind )
		else:
			del link['href']


def download_style_from_link_tag( soup_link, ind ):
	''' 
		Download/save/redirect style loaded with <link href="..../load.php...">
	'''

	link = soup_link
	ind = ind +"# " 
	href = sureUrl( link['href'] )
	print ind+ "stylesheet link found"
	print ind+ "href = "+ href
	if href:
  
		#if href.startswith('//'):
		#	href = 'https:' + href

		(stylename,redirect_path) = download_style( url=href, ind=ind )

		## NOTE: the redirect_path return by download_style needs to be
		##       prepended with a "styles". This is different from the
		##       case of download_imported_style
		redirect_path= os.path.join( "styles", redirect_path) 

		print ind + "Redirect link's style path to: " + redirect_path	
		link['href'] = redirect_path
		print 


def download_imported_style( csstext, ind ):
	''' 
		Download/save style that is originally imported by a css file. The url
		in the "@import url(...)" is redirected to saved file. Return modified csstext.
	'''

	## It turns out that the only css file having imports is with a <link>:
	##
	##	https://en.wikibooks.org/w/load.php?debug=false&lang=en&modules=site&only=styles&skin=vector&*	
	##
	## Its css file contains several lines like this:
	##
	##  @import url(//en.wikibooks.org/w/index.php?title=MediaWiki:Common.css/Autocount.css&action=raw&ctype=text/css) screen;
	##
	## We will extract the url in all @import and save them as style_?.css 

	lines= csstext.split(';')
	for i,ln in enumerate(lines):
		
		if ln.startswith('@import'):

			print ind + ' @import css line found at line #%i'%i
			ln = ln.split( '(')
			ln = [ln[0], ln[1].split(')')[0], ln[1].split(')')[1]]
			url = 'https:' + ln[1]
			(stylename, redirect_path) = download_style( url, ind )

			print ind + "Redirect imported style to " + redirect_path
			lines[i] = ln[0]+'('+ redirect_path + ')' + ln[-1]

	return ';\n'.join( lines )


def download_style( url, ind ):
	''' 
		Download style and update styles buffer. Return (style filename, redirect_path)
	'''

	print ind + ':: Entering download_style( url = "%s ...")'%url[:20]
  
  #	if not url.startswith( url_wiki ):
  #	  print ind + ':: url not starts with url_wiki("%s"), changing it...'%url_wiki
  #	  url = urllib2.urlparse.urljoin( url_wiki, url[0]=="/" and url[1:] or url)
  #	  print ind + ':: New url = '+ url[:20] + '...'
	url = sureUrl( url )  
      
	print ind+ ":: download_style( " + url + " )"	

	if url in styles:
		i= styles.index(url)
		stylename= "style_%s.css"%i
		print ind+ ":: Oh, style " + url
		print ind+ "    already downloaded as: "+ stylename	
	
	else:
		i = len(styles)

		## IMPORTANT: append to styles right after i is retrieved
		styles.append( url ) 

		stylename= "style_%s.css"%i
		print ind+ ":: Assign style name: "+ stylename	
		print ind+ ":: Downloading new style: " + url
		response = urllib2.urlopen(url)
		styletext = response.read()

		styletext= download_imported_style( styletext, ind )

		save_style( stylename, styletext, ind )
		
	redirect_path= os.path.join( '.', stylename) 
		
	return (stylename, redirect_path)	
	

def save_style( stylename, styletext, ind ):
	''' 
		Called by download_style() 
	'''
	path = os.path.join( dir_docs, dir_styles, stylename)
	print ind+ ";; Saving style to : " + path
	open( path, "w" ).write( styletext)


	
def append_style( soup, local_style_path, ind ):
	'''
		Append the style pointed to by local_style_path to soup.head
	'''
	## NOTE: as of 2015.07.14, this function is no longer needed.
	## 		But we keep it here for future reference
	## 
    ##  Note that bs('<link...>') will auto add stuff to make it a
    ##  well formed html doc so we will have to peel an extra layer:
	##
	##  >>> link = bs('<link ...>')
    ##  >>> link
	##  <html><head><link .../></head></html>
	##
	## This is parser dependent: bs('<link ...>', parser_name)
	
	linkdoc = bs('<link rel="stylesheet" type="text/css" href="%s">'% local_style_path)
	link = linkdoc.head.link
	print ind+" Append link to soup.head: "+ str(link)
	soup.head.append( link )



##========================================================
##
##   script
##
##========================================================

def handle_scripts( soup, ind ):
	''' 
		All scripts are shutdown and deleted if possible
	'''

	print ind+ '-'*40
	print ind + '>>> handle_scripts(soup)'
  
	for s in soup.findAll("script"):

		print ind + "Clearing script: " + str(s)
		s.clear()
		try:
			del s['src']
		except: pass
		print ind + "Cleared script: " + str(s)



##========================================================
##
##   tag <a...> (Note: imgs are handled within <a>)
##
## Go thru each <a>, load page or img as needed
##========================================================

def handle_tagAs( soup, ind ):

	print ind+ '>>> handle_tagAs(soup)'
	for a in soup.find_all('a'):
		href= a.get('href')
		'''
		href could be:

		https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/First_Steps
		https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/First_Steps/Creating_a_simple_model
		
		But we save all pages in the folder where the home page is anyway.
		'''
		
		if a.string=='edit': # Remove [<a...>edit</a>] 
			a.findParents()[0].clear()

		elif href:
			if href.startswith(url_openscadwiki):

				fnames = href.split("/")[-1].split("#") # like: aaa#bbb=> [aaa,bbb]
				fname  = fnames[0]+".html"
				fnamebranch = fname + (len(fnames)>1 and ("#"+fnames[1]) or "")  # like: aaa.html#bbb
				
				if not fname=='Print_version.html':

					handle_page(url=href, indent=len(ind)+2)
					a['href']= fnamebranch
					print ind+ "Saved page as = ", os.path.join(dir_docs, fname)
					print ind+ "New href = ", a.get('href')
					print ind+ "Total pages= ", len(pages) 

      
			elif href.startswith('/wiki'):
				a['href']= url_wiki + href
			elif href.startswith('//'):
				a['href']= 'https:' + href

			if a.img and not a.img['src'].startswith( '/static/images' ):
			
				imgname = download_img( soup_a=a, ind=ind+"| " )
				redirect_img( a, imgname, ind )


##========================================================
##
##   img 
##
## All imgs are wrapped inside <a>, so download_img() is
## called when handling <a> (handle_tagAs)
##========================================================

def download_img( soup_a, ind ):
	''' 
		Download an image in <a...><img ...></a>. Return imgname

		soup_a: a BeautifulSoup tag class
		ind   : indent for logging
	'''
	
	print ind+ '-'*40
	print ind+ '>>> download_img(soup_a)'
	src = sureUrl( soup_a.img['src'] )
#	if src.startswith('//'):
#	   src = "https:" + src
#	elif not src.startswith( url_wiki):
#	  src = urllib2.urlparse.urljoin( url_wiki, src)

	imgname = src.split("/")[-1]

	# Decode url:
	#  Some img name contains %28,%29 for "(",")", resp, and %25 for %.
	imgname = imgname.replace('%28','(').replace('%29',')').replace('%25','%')

	print ind+ "Img src: " + src

	savepath = os.path.join( dir_imgs, imgname)  # local img path
	if not savepath in imgs:
	
		print ind+"Downloading: "+ imgname
		urllib.urlretrieve( src , savepath )		# download image
		imgs.append( savepath )
		print ind+"Saved img as: "+savepath

	# Remove srcset that seems to cause problem in some Firefox
	del soup_a.img['srcset'] 

	# For debug:
	# print ind+ "a.img: "+str(a)	

	return imgname 


def redirect_img( soup_a, imgname, ind ):
	''' 
		Redirect img src links in soup_a (<a...><img ...></a>) to local path.
 
		soup_a: a BeautifulSoup tag class
		ind   : indent for logging
	'''
	linkurl = os.path.join( '.', 'imgs', imgname) # ./imgs/img.png
	print ind+"Img links redirect to: "+linkurl	
	soup_a.img['src'] = linkurl
	soup_a['href']= linkurl
	print ind+"Total imgs: "+ str(len(imgs))

	# For debug:
	# print ind+ "a.img: "+str(a)	

	print ind+ '-'*40

##========================================================
##
##   misc
##
##========================================================

def getFooterSoup( pageurl, pagename ):
	'''
		Return a BeautifulSoup tag as a footer soup
	'''	
	A = '<a style="color:black" href="%s">%s</a>'

	A_page = A%( pageurl.split("#")[0], pagename.split(".")[0] )
	A_license= A%("http://creativecommons.org/licenses/by-sa/3.0/"
			   ,"Creative Commons Attribution-Share-Alike License 3.0"
			   )
	A_offliner= A%(url_offliner, "openscad_offliner")
	
	footer= (
		'''<div style="font-size:13px;color:darkgray;text-align:center">
		Content of this page is extracted on %(date)s from the online OpenSCAD 
		Wikipedia article %(page)s (released under the %(license)s)
		using %(offliner)s
		</div>'''
	)%{ "page": A_page
	  , "license": A_license
	  , "offliner": A_offliner
	  , "date": (time.strftime("%Y/%m/%d %H:%M"))
	  }

	return bs(footer)
 

def removeNonOpenSCAD( soup ):
	'''
		Given the whole soup, remove non OpenSCAD parts
	'''
	for elm in soup.findAll("noscript"): elm.clear()
	
	unwanted_div_classes = ["printfooter","catlinks","noprint"]
	unwanted_table_classes= ['noprint','ambox']

	for kls in unwanted_div_classes: 
		for elm in soup.findAll('div', kls):
			elm['style']="display:none" 
			elm.clear()
	for kls in unwanted_table_classes: 
		for elm in soup.findAll('table', kls): 
			elm.clear()
			elm['style']="display:none"


	# Get rid of wiki menu and structure		
	content = soup.find(id='content')
	content['style']= "margin-left:0px"
	soup.body.clear()
	soup.body.append( content )


##========================================================
##
##   html page --- this is the main function
##
##========================================================

def handle_page( url=url,folder=dir_docs, indent=0 ):	


	# For logging	
	ind = ' '*indent+'['+str(len(pages)+1)+'] '
	indm = ind +"| " # for image

	print ind+ ':'*40
	print ind+ '>>> handle_page(url="%s", folder="%s")'%(url, folder)
	#print ind+ 'Page: ' + href
					
	
#	if not url.startswith( url_wiki):
#		url = url_wiki + url 
	url = sureUrl( url )  
	
	if url not in pages: # url not already downloaded

		print ind+'===================================='
		print ind+'This page not yet loaded, load to Page # ', len(pages)+1
		print ind+'Downloading:', url #.split('/')[-1]

		response = urllib2.urlopen(url)
		html = response.read()
		pages.append( url )
		
		soup = bs(html, 'html.parser')

		handle_styles( soup, ind )

		handle_tagAs( soup, ind )

		handle_scripts( soup, ind )

		removeNonOpenSCAD( soup )

		fname = url.split("/")[-1].split("#")[0]+".html"
		soup.body.append( getFooterSoup( url, fname ) )	

		#=======================================
		# Save html
		#=======================================
		filepath = os.path.join( folder, fname)
		print ind+"Saving: ", filepath
		open(filepath, "w").write( str(soup) )
		print ind+"# of pages: ", len(pages)
		print ind+"# of styles: ", len(styles)
		print ind+"# of imgs: ", len(imgs)
		print 
		
	'''# for debugging	
	if len(pages)==94:
		for s in styles:
			print 
			print 
			print s
	'''


handle_page(folder=dir_docs)


__history__={
 "20150708":"First working draft"
,"20150712":
	(
	 ('* it fires of a number of JavaScripts that access the Wikibooks site','Fixed: all javascripts shut down')
	,('* all the CSS files are loaded online','Fixed: all css downloaded')
	,("* most of the images don't work (at least in Firefox) as they have a srcset attribute (which I did not even know until just now)","srcset deleted")
	,('* the index looks strange due to missing SVG files','Fixed')
	,("* the chapter links into other pages don't work",'Fixed') 
	,('* the edit links are displayed as []','Fixed')
	,('* better to add .html to all file names','Fixed')
	)
,"20150714":
	( "Major restructuring into smaller pieces", "Able to load @import styles")
,"20160320":
	( "Major fix for bug believed to be a cross-platform issue. The original version, which is developed in Linux, is saved as openscad_offliner_2015.py. It is made to work in Windows in the current version.")
}


