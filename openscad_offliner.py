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

'''

import urllib, urllib2, os, time
from bs4 import BeautifulSoup as bs

#
# Set main and img folders:
#
dir_docs = 'openscad_docs'                       
dir_imgs =  os.path.join( dir_docs, 'imgs')  

#
# Data url
#
url_site= 'https://en.wikibooks.org'
url = 'https://en.wikibooks.org/wiki/OpenSCAD_User_Manual'
url_wiki = 'https://en.wikibooks.org'
url_opscad = '/wiki/OpenSCAD_User_Manual'


footer = bs(
'''<hr width=1 /><div style="font-size:14px;color:darkgray;text-align:center">
Downloaded from <a href="%s">here</a> with <b style="color:blue">%s</b> 
on ( <u style="color:blue">%s</u> )
</div><br/><br/><br/>'''%( url, __file__, (time.strftime("%Y/%m/%d %H:%M")) )
)

if not os.path.exists(dir_docs): os.makedirs(dir_docs)
if not os.path.exists(dir_imgs): os.makedirs(dir_imgs)

pages= [] # Names of downloaded pages
imgs = [] # Local paths of downloaded images


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
			
			if a.string=='edit': # Turn [edit] to []
				a.string=''
			elif href:
				if href.startswith(url_opscad):
 
					fname = href.split("/")[-1].split("#")[0]
					
					if not fname=='Print_version':

						print ind+ ':'*40
						print ind+ 'Page: ' + href
						loadOpenSCADHelp(url=href, indent=indent+2)
						a['href']= fname
						print ind+ "Saved page as = ", os.path.join(dir_docs, fname)
						print ind+ "New href = ", a.get('href')
						print ind+ "Total pages= ", len(pages) 

				elif href.startswith('/wiki'):
					a['href']= url_site + href
				elif href.startswith('//'):
					a['href']= 'https:' + href


				if a.img and not a.img['src'].startswith( '/static/images' ):
				
					src = a.img['src']
					if src.startswith('//'):
					   src = "https:" + src

					imgname = src.split("/")[-1]
					# Some img contains %28,%29 for "(",")", resp.
					imgname = imgname.replace('%28','(').replace('%29',')')
					imgpath = os.path.join( dir_imgs, imgname)  # local img path

					print indm+ '-'*40
					print indm+ "Img src: " + src

					print indm+"Downloading: "+ imgname

					if not imgpath in imgs:
					
						urllib.urlretrieve( src , imgpath )		# download image
						imgs.append( imgpath )

					#
					# Modify links in <a> and <img> to point to local imgs.
					# Note that this has to be done even if imgpath already 
					# in imgs (means the img was downloaded previously) cos
		            # some imgs are used more than once. If we don't do this
					# on the 2nd round, the a and img links will fail
					#
					a.img['src'] = imgpath.replace( dir_docs,'.') 
					a['href']= imgpath.replace( dir_docs,'.')
					print indm+"Saved img as: "+imgpath
					print indm+"Total imgs: "+ str(len(imgs))
				
					# For debug:
					# print indm+ "a.img: "+str(a)	

					print indm+ '-'*40
				

		#
		# Adjust <link...> to make css work
		#
		for link in soup.find_all('link'):
			href= link.get('href')
			if href and href.startswith('//'):
				link['href'] = 'https:' + href

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

		# Hide the wiki categories links 
		soup.find('div', id='catlinks')['style']="display:none"

		# Get rid of wiki menu and structure		
		content = soup.find(id='content')
		content['style']= "margin-left:0px"
		soup.body.clear()
		soup.body.append( content )	
		soup.body.append( footer )	
		#=======================================


		# 
		# Save doc
		#
		filename = os.path.split(url)[-1]
		filename = filename.split("#")[0]
		filepath = os.path.join( folder, filename)

		print ind+"Saving: ", filepath
		open(filepath, "w").write( str(soup) )
		print 
		print ind+"# of pages: ", len(pages)
		print ind+"# of imgs: ", len(imgs)




loadOpenSCADHelp(folder=dir_docs)
