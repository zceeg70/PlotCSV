from distutils.core import setup
import csv
import sys
import os.path
import json
import matplotlib.pyplot as plt
#plt.use("Agg")
#setup(options={'py2exe':{'excludes':['_gtkagg','_tkagg']}})
from datetime import datetime
import time


class ConfigClass:
    def __init__(self):
        self.plots = []
        self.csvs = []
        self.csvNames = []
        self.filename = ""
        
    def attachKeys(self,keys):
        pass

    def extract(self,configDict):
        plots = self.plots
        csvs = self.csvs
        csvNames = self.csvNames
        expectedKeys = {"plots":plots,"csvs":csvs} #{"plots":plots,"csvs":csvs}
        for key in expectedKeys:
            #print("Expected Key: %s"%(key))
            if key in configDict:
                print("Found Key: %s, Value: %s"%(key,configDict[key]))
                #print(configDict[key])
                expectedKeys[key] = configDict[key]
            else:
                print("Key '%s' not found"%(key))
                sys.exit()
        for plotArg in expectedKeys["plots"]:
            self.plots.append(plotArg)
        #self.plots = expectedKeys["plots"]
        #print(plots)
        for csvArg in expectedKeys["csvs"]:
            self.csvs.append(csvArg)
        #self.csvs = expectedKeys["csvs"]
        self.plottingEnabled = configDict["plottingEnabled"]
        self.csvWriteEnabled = configDict["csvEnabled"]
        self.filename = configDict["CSV_to_load"]
        
        self.csvNames = configDict["csvOutputFile"]
        
def loadConfig():
    configFileName = "SPOLogPlotterConfig.txt"
    if not os.path.isfile(configFileName):
        print("No config file found. Expected %s"%(configFileName))
        sys.exit()
    configuration = open(configFileName,'r').read()
    configDict = json.loads(configuration)
    #
    configuration = ConfigClass()
    configuration.extract(configDict)
    return configuration
    
class load: # loads a CSV
    def __init__(self,filename,callback=None):
        self.filename = filename
        self.headers = []
        with open(self.filename,"r") as csvfile:
            datareader = csv.reader(csvfile)
            #print(datareader)
            for row in datareader:
                headers = row
                break
        self.headers = headers
            #headers = row in datareader
        data = []
        self.data = data
        if not callback == None:self.callback = callback

    def read(self): # Read CSV
        start = time.time()
        with open(self.filename,'r') as file:
            reader = csv.reader(file)
            data = self.data
            for row in reader:
                data.append(row)
        self.data = data
        self.headers = data[0]
        end = time.time()
        print("Time to load CSV:%f"%(end-start))
        print("Read %d lines from '%s'"%(len(data),self.filename))

    def getColumnByHeader(self,header):
        #start = time.time()
        if not header in self.headers: return
        indexHeader = self.headers.index(header)
        #print(indexHeader)
        with open(self.filename,"r") as csvfile:
            datareader = csv.reader(csvfile)
            count = 0
            outputStuff = []
            for index, row in enumerate(datareader):
                if ":" in row[indexHeader] or "Timestamp" in header or index==0:
                    outputStuff.append(row[indexHeader])
                else:
                    outputStuff.append(float(row[indexHeader]))
                #if index == 20: return outputStuff
        return outputStuff
        
    def save(self,dataset,path):
        if os.path.isfile(path): return "Path already exists (or has no extension)"
        csv_file = open(path,"w")
        try:
            if not(type(dataset) is list): return "Dataset must be a list"
            writer = csv.writer(csv_file,delimiter=',')
            for line in dataset:
                #print(line)
                if type(line) is list: writer.writerow(line)
                else: writer.writerow([line,])
        finally:
            csv_file.close()

        return "Data saved successfully"

class plotHandler:
    def __init__(self, config, CSV):
        self.config = config
        self.CSV = CSV

    def writeAll(self):
        timeStart = time.time()
        CSV = self.CSV
        config = self.config
        csvs = config.csvs
        outputFile = []
        outputFile = config.csvNames
        print("Asked to write: %s"%(outputFile))
        Column = []
        for index,csv in enumerate(csvs):
            print("Writing csv: %s"%(csv))
            csvData = []
            for header in csv:
                # for each header specified for a given plot
                if not header in CSV.headers:
                    print("Header '%s' not found..skipping"%(header))
                else:
                    #print("Header '%s' found"%(header))
                    indexHead = CSV.headers.index(header)
                    tempData = CSV.getColumnByHeader(header)
                    if "Timestamp" in header:
                        Column.append(convertTime(tempData))
                        timeData = Column[0]
                        csvData.append(tempData)
                        timeData[0] = "DeltaTime"
                        csvData.append(timeData)
                    else:
                        csvData.append(tempData)
                    Column = []
            if len(csvData)>0:
                csvData = mergeForCSV(csvData)
                saveOutcome = CSV.save(csvData,outputFile[index][0])
                print("Save outcome: %s"%(saveOutcome))
    
    def plotAll(self):
        timeStart = time.time()
        CSV = self.CSV
        config = self.config
        plots = config.plots
        Column = []
        plotData = []
        ColourWheel = {0:'r',1:'g',2:'b',3:'k',4:'m',5:'o',6:'y'}
        timeData = []
        cheatyHack = 0
        for indexPlot,plot in enumerate(plots):
            print("Starting to plot: %s"%(plot))
            items = []
            if len(plotData)>0:
                plotData = []
            for header in plot: # for each header specified for a given plot
                if not header in CSV.headers:
                    print("Header '%s' not found..skipping"%(header))
                else:
                    print("Header '%s' found"%(header))
                    indexHead = CSV.headers.index(header)
                    tempData = CSV.getColumnByHeader(header)
                    if "Timestamp" in header:
                        Column.append(convertTime(tempData))
                        timeData = Column[0]
                    else:
                        plotData.append(tempData)
                    Column = []
            if len(plotData)>0:
                if not "Timestamp" in plot:
                    timeData = plotData.pop(0)
                plt.close(0)
                print("Plotting figure(%d)"%(indexPlot))
                plt.figure(indexPlot)
                fig,axes = plt.subplots()
                for indexPlotData,dataSet in enumerate(plotData):
                    items.append(axes.plot(timeData[1:],dataSet[1:],\
                                          ColourWheel[indexPlotData],\
                                          label=dataSet[0]))
                    print("plotted:%s"%(dataSet[0]))
                axes.set_xlabel(timeData[0])
                axes.set_title(plot)
                axes.legend(handles = items,labels = [])
                axes.grid(True)
                axes.legend(bbox_to_anchor = (0.1,.522,1.5,.102),loc=9)
                #plotData = []
                #print(len(plotData))
                for dataset in plotData:
                    plotData.remove(dataset)
                #cheatyHack = dataset
                #print(cheatyHack)
                #print(plotData)
            #plotData = []
        timeFinish = time.time()
        print("Plotting took %d seconds"%(timeFinish-timeStart))
        plt.show()

def convertTime(timeArray):
    if type(timeArray) is list:
        timeFormat = "%Y-%m-%d %H:%M:%S.%f"
        timeArrayLength = len(timeArray)
        timeStart = datetime.strptime(timeArray[1],timeFormat)
        convertedTime = []
        convertedTime.append(timeArray[0])
        for index,row in enumerate(timeArray):
            if index == 0: continue
            currentTime = datetime.strptime(row,timeFormat)
            difference = (currentTime - timeStart).total_seconds()
            #print(difference)
            convertedTime.append(difference)
    else:
        print("Returning from convertTime as no list was found")
        return
    return convertedTime

def parseTimeStamp(stamp,resolution="seconds"):
    #if not " " in stamp: return #Gets rid of first line headers
    if not type(stamp) is list: return
    #Input time format as 2014-11-04 15:14:32.765
    Header = stamp[0]
    for index,row in enumerate(stamp):
        if index == 0: continue
        Parts = stamp[index].split(" ")
        Date, Time = Parts[0], Parts[1]
        DateTokens = Date.split("-")
        Day = DateTokens[2]
        TimeTokens = Time.split(":")
        time = int(Day)*(60*60*24)+int(TimeTokens[0])*3600+\
               int(TimeTokens[1])*60+float(TimeTokens[2])
        if index == 1:
            startDate = "-".join(DateTokens)
            startTime = time
        stamp[index] = time - startTime
        
    endDate = "-".join(DateTokens)
    dateSpan = [startDate,endDate]
    
    return [stamp,dateSpan]

def orderData(Dataset):
    if not type(Dataset) is list: return
    if not len(Dataset[0])>1: return

    
def combine(string1, string2):
    result = []
    for rowa,rowb in zip(string1,string2):
        result.append([rowa,rowb])
    return result

def mergeForCSV(toMergeList): #multiple columns of data
    dataLength = len(toMergeList[0])
    result = []
    subList = []
    for index, row in enumerate(toMergeList[0]):
        for lists in toMergeList:
            subList.append(lists[index])
        result.append(subList)
        subList = []
    #print(result)
    return result

def keyStats():
    pass
    

def main():
    filename = 'spo-nx_calibration.log'
    Configuration = loadConfig()
    #filename = Configuration['CSV']
    #print(Configuration)
    filename = Configuration.filename
    CSV = load(filename)
    #CSVData_Raw = CSV.read()
    output = plotHandler(Configuration,CSV)
    if Configuration.plottingEnabled:
        output.plotAll()
    if Configuration.csvWriteEnabled:
        output.writeAll()

    
if __name__ == "__main__":
    main()
