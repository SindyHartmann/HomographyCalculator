import csv
#fileformat: time,[playerid, x,y, confidence?]
class CSV:
    writer = None
    reader = None
    fileName = 'test'
    currentTime = None
    lines = 0
    def __init__(self, fileName = 'test'):
        self.fileName = fileName
        #self.initWriter(self.fileName)


    def initWriter(self, fileName):
        with open(fileName+'.csv', mode='w') as data_file:
            self.writer = csv.writer(data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    def writeLine(self, line):
        print(self.fileName)
        print(self.lines)
        if self.lines == 0:
            writemode = 'w'
        else:
            writemode = 'a'
        print(writemode)
        with open(self.fileName+'.csv', mode=writemode, newline='') as data_file:
            self.writer = csv.writer(data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            #TODO: Check if Line is iterable
            self.writer.writerow(line)
            data_file.close()
        self.lines+=1

    def writeLines(self, lines):
        if self.writer is not None:
            #TODO:
            self.writer.writeLines(lines)

    def writeFrame(self, time, ids, positions, confidences):
        if len(ids) == len(positions)==len(confidences):
            players = []
            print("len")
            print(len(ids))
            for i in range(len(ids)):
                players.append(str(ids[i]))
                players.append(str(positions[i][0]))
                players.append(str(positions[i][1]))
                players.append(str(confidences[i]))
            self.writeLine([str(time)]+players)
            return 1
        else:
            return -1
            #TODO: positions is list of list!
            #players = [y for x in zip(ids, positions) for y in x]

