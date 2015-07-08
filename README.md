# openscad_offliner
Download OpenSCAD online documentation for offline reading.

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
