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

import urllib, urllib2, os, time
from bs4 import BeautifulSoup as bs

#
# Set folders:
#
dir_docs = 'openscad_docs'                       
dir_imgs =  os.path.join( dir_docs, 'imgs')  
dir_styles =  'styles'   
dir_styles_full = os.path.join( dir_docs, 'styles')  

if not os.path.exists(dir_docs): os.makedirs(dir_docs)
if not os.path.exists(dir_imgs): os.makedirs(dir_imgs)
if not os.path.exists(dir_styles_full): os.makedirs(dir_styles_full)
print "dir_docs= " + dir_docs
print "dir_imgs= " + dir_imgs
print "dir_styles= " + dir_styles
print "dir_styles_full= " +dir_styles_full

#
# Data url
#
url_site= 'https://en.wikibooks.org'
url = 'https://en.wikibooks.org/wiki/OpenSCAD_User_Manual'
url_wiki = 'https://en.wikibooks.org'
url_opscad = '/wiki/OpenSCAD_User_Manual'
url_offliner= 'https://github.com/runsun/openscad_offliner'

#
# footer
#
footer = bs(
'''<hr width=1 />
<div style="font-size:14px;color:darkgray;text-align:center">
Downloaded from <a style="color:darkgray" href="%s">here</a> 
with <a style="color:darkgray" href="%s">%s</a> 
on ( <span style="color:darkgray">%s</span> )
</div><br/><br/><br/>'''%( url
						 , url_offliner
						 , __file__.split(".")[0]
						 , (time.strftime("%Y/%m/%d %H:%M")) )
)

#
# Buffer to keep track of downloaded to avoid repeat downloads
#
pages= [] # Urls of downloaded pages
imgs = [] # Local paths of downloaded images (except ** common_styles ** )
styles=[] # stylesheet urls


def download_img( soup_a, ind ):
	
	src = soup_a.img['src']
	if src.startswith('//'):
	   src = "https:" + src

	imgname = src.split("/")[-1]

	# Decode url:
	#  Some img name contains %28,%29 for "(",")", resp, and %25 for %.
	imgname = imgname.replace('%28','(').replace('%29',')').replace('%25','%')

	imgpath = os.path.join( dir_imgs, imgname)  # local img path

	print ind+ '-'*40
	print ind+ "Img src: " + src

	print ind+"Downloading: "+ imgname

	if not imgpath in imgs:
	
		urllib.urlretrieve( src , imgpath )		# download image
		imgs.append( imgpath )

	# Remove srcset that seems to cause problem in some Firefox
	del soup_a.img['srcset'] 

	# Modify links in <a> and <img> to point to local imgs.
	# Note that this has to be done even if imgpath already 
	# in imgs (means the img was downloaded previously) cos
    # some imgs are used more than once. If we don't do this
	# on the 2nd round, the a and img links will fail
	soup_a.img['src'] = imgpath.replace( dir_docs,'.') 
	soup_a['href']= imgpath.replace( dir_docs,'.')
	print ind+"Saved img as: "+imgpath
	print ind+"Total imgs: "+ str(len(imgs))

	# For debug:
	# print indm+ "a.img: "+str(a)	

	print ind+ '-'*40


def download_common_styles(soup,ind):
	'''Download common styles that are in 

		https://en.wikibooks.org/w/index.php?title=MediaWiki:Common.css
			/Lists.css&action=raw&ctype=text/css
			/Messages.css&action=raw&ctype=text/css
			/Media.css&action=raw&ctype=text/css
			/Multilingual.css&action=raw&ctype=text/css
			/Nav.css&action=raw&ctype=text/css
			/search.css&action=raw&ctype=text/css
			/toc.css&action=raw&ctype=text/css
			/top.css&action=raw&ctype=text/css
			/Slideshows.css&action=raw&ctype=text/css

		(check out the page Positioning_an_object.html)

		They seem to be loaded by 

        <script src="//en.wikibooks.org/w/load.php?debug=false&amp;
          lang=en&amp;modules=startup&amp;only=scripts&amp;skin=vector&amp;*">
        </script>

	    and hard to retrieve. So we use brutal forces to get them one by one 
		and store them all together in the file style_common.css

		This download only performs when styles=[], means at the startup
		of process. 

		The addition of link to style_common.css, however, is performed on
		every page. 
	'''
	
	baseurl = 'https://en.wikibooks.org/w/index.php?title=MediaWiki:Common.css'
	urls = [ '/Lists.css&action=raw&ctype=text/css'
			,'/Messages.css&action=raw&ctype=text/css'
			,'/Media.css&action=raw&ctype=text/css'
			,'/Multilingual.css&action=raw&ctype=text/css'
			,'/Nav.css&action=raw&ctype=text/css'
			,'/search.css&action=raw&ctype=text/css'
			,'/toc.css&action=raw&ctype=text/css'
			,'/top.css&action=raw&ctype=text/css'
			,'/Slideshows.css&action=raw&ctype=text/css'
			]

	style_str= "// [openscad_offliner]: \n" \
			 + "//  Common styles that -- if on the web -- are downloaded \n" \
			 + "//  by script: \n" \
			 + "//   //en.wikibooks.org/w/load.php?debug=false&amp;lang=en&amp;modules=startup&amp;only=scripts&amp;skin=vector&amp;*" \
			 + "\n"
	
	#
	# Download
	#	
	savepath= os.path.join(dir_styles_full, "style_common.css")
	
	if not styles:
		print ind+"Loading common styles:"
		for u in urls:
			u = baseurl+u
			print ind+"  Loading: "+u
			response = urllib2.urlopen(u)
			s = response.read()
			style_str = "\n" +style_str + "\n// [openscad_offliner]: From:"+ u + "\n"+ s + "\n\n"
		
		#linkurl = dir_styles+"/style_common.css"
		print ind+" Save to: " + savepath
		open( savepath,"w").write(style_str)

	appendStyle( soup, local_style_path= savepath, ind=ind )
	'''
	# Append style_common.css to soup
	# 
    #  Note that bs('<link...>') will auto add stuff to make it
    #  a well formed html doc
	#
	#  >>> link = bs('<link ...>')
    #  >>> link
	#  <html><head><link .../></head></html>
	#
	# This is parser dependent: bs('<link ...>', parser_name)
	#  
	linkurl = dir_styles+"/style_common.css"
	linkdoc = bs('<link rel="stylesheet" type="text/css" href="%s">'% linkurl)
	link = linkdoc.head.link
	print ind+" Append link to soup.head: "+ str(link)
	soup.head.append( link )
	'''

def download_style( soup_link, ind ):

	link = soup_link
	ind = ind +"# " 
	href = link['href']
	print ind+ "stylesheet link found"
	print ind+ "href = "+ href
	if href:
		if href.startswith('//'):
			href = 'https:' + href

		if href in styles:
			style_idx = styles.index(href)
			stylename = "style_%s.css"%( style_idx )
			redirect_path= os.path.join( dir_styles, stylename) 
			print ind +"style already in styles[%s], setting stylenames= %s"%(style_idx, stylename)
			

	   	else:
			styles.append( href )
			
			response = urllib2.urlopen(href)
			style = response.read()
			stylename = "style_%s.css"%(len(styles))
			redirect_path= os.path.join( dir_styles, stylename) 
			save_path = os.path.join( dir_styles_full, stylename) 
			print ind +"New style found, saved as = %s"%(save_path)
			open(save_path, "w").write( str(style) )

		print "Redirect path to: " + redirect_path	

		link['href'] = redirect_path
		print 
		print ind+"# of styles: ", len(styles)

	
def appendStyle( soup, local_style_path, ind ):
	'''
	# Append to soup.head
	# 
    #  Note that bs('<link...>') will auto add stuff to make it
    #  a well formed html doc
	#
	#  >>> link = bs('<link ...>')
    #  >>> link
	#  <html><head><link .../></head></html>
	#
	# This is parser dependent: bs('<link ...>', parser_name)
	'''  
	linkdoc = bs('<link rel="stylesheet" type="text/css" href="%s">'% local_style_path)
	link = linkdoc.head.link
	print ind+" Append link to soup.head: "+ str(link)
	soup.head.append( link )


def stop_scripts( soup, ind ):
	''' 
		Some scripts don't seem to be needed so we stop them 
	'''

	ss=["//en.wikibooks.org/w/load.php?debug=false&amp;lang=en&amp;modules=startup&amp;only=scripts&amp;skin=vector&amp;*"
	   ]
	for s in soup.findAll("script"):

		print ind + "Clearing script: " + str(s)
		s.clear()
		try:
			del s['src']
			#if 'src' in s and "startup" in s['src']:
			#	s['src']=''
		except: pass
		print ind + "Cleared script: " + str(s)
		'''
		print ind+"Found script: " + str(s)
		
		if 'src' in s and "startup" in s['src']:
		#if s.src in ss:
			print ind+"Stopping script: " + s['src']
			s['src']='' 
		'''
	

def loadOpenSCADHelp(url=url,folder=dir_docs, indent=0):	

	# For log	
	ind = ' '*indent+'['+str(len(pages)+1)+'] '
	indm = ind +"| " # for image
	
	if not url.startswith( url_wiki):
		url = url_wiki + url 
	
	if url not in pages:

		print 
		print ind+'===================================='
		print ind+'Page # ', len(pages)+1
		print ind+'Downloading:', url #.split('/')[-1]


		response = urllib2.urlopen(url)
		html = response.read()
		pages.append( url )
		
		soup = bs(html, 'html.parser')
		allas = soup.find_all('a')
		
		for a in allas:
			href= a.get('href')
			'''
			href could be:

				https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/First_Steps
				https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/First_Steps/Creating_a_simple_model
				
				if 2nd case, need create folder. But to make it simple, we save 
				all pages in the folder where the home page is
			'''
			
			if a.string=='edit': # Remove [<a...>edit</a>] 
				a.findParents()[0].clear()

			elif href:
				if href.startswith(url_opscad):
 
					fnames = href.split("/")[-1].split("#") # like: aaa#bbb=> [aaa,bbb]
					fname  = fnames[0]+".html"
					fnamebranch = fname + (len(fnames)>1 and ("#"+fnames[1]) or "")  # like: aaa.html#bbb
					
					if not fname=='Print_version.html':

						print ind+ ':'*40
						print ind+ 'Page: ' + href
						loadOpenSCADHelp(url=href, indent=indent+2)
						a['href']= fnamebranch
						print ind+ "Saved page as = ", os.path.join(dir_docs, fname)
						print ind+ "New href = ", a.get('href')
						print ind+ "Total pages= ", len(pages) 

				elif href.startswith('/wiki'):
					a['href']= url_site + href
				elif href.startswith('//'):
					a['href']= 'https:' + href

				if a.img and not a.img['src'].startswith( '/static/images' ):
				
					download_img( soup_a=a, ind=indm ) 
								

		# NOTE: common styles are downloaded when styles=[], means, at startup
		# So, do not move this below the "Adjust <link...> below, otherwise 
		# common styles will not be downloaded
		download_common_styles(soup, ind=ind)
		
		#
		# Adjust <link...> to make css work
		#
		for link in soup.find_all('link'):

			href = link.get('href')
			if '/load.php?' in href:
				download_style( soup_link=link, ind=ind )
			else:
				del link['href']


			# href= link.get('href')
			# if href and href.startswith('//'):
			#	link['href'] = 'https:' + href

#<link href="https://en.wikibooks.org/w/load.php?debug=false&amp;lang=en&amp;modules=ext.flaggedRevs.basic%7Cext.inputBox.styles%7Cext.uls.nojs%7Cext.visualEditor.viewPageTarget.noscript%7Cext.wikihiero%7Cmediawiki.legacy.commonPrint%2Cshared%7Cmediawiki.sectionAnchor%7Cmediawiki.skinning.interface%7Cmediawiki.ui.button%2Ccheckbox%2Cinput%7Cskins.vector.styles%7Cwikibase.client.init&amp;only=styles&amp;skin=vector&amp;*" rel="stylesheet"/>
# <meta content="" name="ResourceLoaderDynamicStyles"/>
#<link href="https://en.wikibooks.org/w/load.php?debug=false&amp;lang=en&amp;modules=site&amp;only=styles&amp;skin=vector&amp;*" rel="stylesheet"/>

		#=========================================
		#
		# Remove or hide non-OpenSCAD parts:
		#
		elm_noprint = soup.find_all('div', class_='noprint')
		print ind+ "elm_noprint: %s"%len(elm_noprint) 
		for elm in elm_noprint: 
			elm.clear()
			elm['style']="display:none"
			print ind+ "After clear: elm = "+str(elm)

		badtableclasses = ['noprint','ambox']
		for cls in badtableclasses:
			badtables = soup.find_all('table', class_=cls) 
			for elm in badtables: 
				elm.clear()
				elm['style']="display:none"
				#print ind+ "After clear: elm = "+str(elm)


		stop_scripts(soup, ind=ind)

	
		# Hide the wiki categories links 
		soup.find('div', id='catlinks')['style']="display:none"

		# Get rid of wiki menu and structure		
		content = soup.find(id='content')
		content['style']= "margin-left:0px"
		# content = bs(  str( content).replace("[]","") )
		soup.body.clear()
		soup.body.append( content )	
		soup.body.append( footer )	
		#=======================================

		# 
		# Save doc
		#
		filename = os.path.split(url)[-1]
		filename = filename.split("#")[0]
		filepath = os.path.join( folder, filename+'.html')

		print ind+"Saving: ", filepath
		open(filepath, "w").write( str(soup) )
		print 
		print ind+"# of pages: ", len(pages)
		print ind+"# of styles: ", len(styles)
		print ind+"# of imgs: ", len(imgs)
		
		
	if len(pages)==94:
		for s in styles:
			print 
			print 
			print s

loadOpenSCADHelp(folder=dir_docs)

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
	)
}


