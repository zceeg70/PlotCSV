READ ME:: PLOT CONTROL


Included with this script is a config file (PlotControlConfig.txt). 

** V. Important**
The config file is very important. Keep formatting identical.

The script loads this as a JSON object - it is sensitive to formatting.
Google will help with any errors that point to the config file.

Will NOT run on python 2.7 without proper install of matplotlib (needs the 32-bit edition)


** To change the plots **
In the config file is 

"plots":[
	['default1','default2'],
	['default1','default3,'default4']
	]

change/add/remove lines in this 'array' (called a list in python) by typing in the
		EXACT header of that which you wish to plot.
The first argument given will be the xaxis (though I've written it to auto-detect the
	Timestamp field but not tested that thoroughly)
Timestamp is automatically converted into deltaTime - which is in seconds and is the time
since the start of the test.

** Generate CSVS **
"csvs": generates CSVs with all the arguments given in the same way as "plots"

If asked to save Timestamp it will also save delta Time. 


** Good luck **

