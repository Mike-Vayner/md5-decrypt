# main
    # communication
        # send
        # recv
    # bruteforce
        # bf threads


# > amogus
# < num: _ _
# > num: _ _
# < start:######,stop:######,md5:########
# > ok

# check

# > failed:end / success:###### / failed:next
# < ok                          / go back to line 12

# < end:success,time:###


import socket
import threading
import queue
import hashlib
#import bruteforceMD5 as mdCode


messages = queue.Queue()
task = None         # what to do
password = None     # found password
checked = False     # was string checked
found = False       # was string found
stopThread = False  # stop all searching threads
stopRun = False


def communicationFunc():
    print('run')
    soc = socket.socket()
    soc.connect(('10.30.56.235', 9999))
    print('connected to server')
    sendThr = threading.Thread(target=sendComFunc, args=(soc,))
    recvThr = threading.Thread(target=recvComFunc, args=(soc,))
    sendThr.start()
    recvThr.start()
    sendThr.join()
    recvThr.join()
    soc.close()


def sendComFunc(soc):
    global messages
    global found
    global password
    global stopThread
    global stopRun
    global checked

    print('sending message')
    soc.send('amogus'.encode())
    # tututututututu tututu 
    # pam pam
    
    run = True
    while run:
        print('inside while in sendcomfunc')
        if checked:
            print('checked')
            if found:
                answer = 'success:' + password
            else:
                answer = 'failed:end'
            print('answer after decryption: ' + answer)
            soc.send(answer.encode())
            password = None
            checked = False
            found = False
            stopThread = False
        else:
            print('waiting to get message')
            message = messages.get()
            print('got message: ' + message)
            answer = handleMessage(message)
            if answer is not False:
                soc.send(answer.encode())
            else:
                stopRun = True
                run = False

def handleMessage(message):
    if str.startswith(message, 'end:success,time:') or message == 'ok':
        # end this business
        return False
    elif str.startswith(message, 'num:'):
        # id
        return message
    elif str.startswith(message, 'start:'):
        global task
        # start decoding (append into global variable)
        task = message
        return 'ok'


def recvComFunc(soc):
    global messages
    global stopRun
    while True and not stopRun:
        message = soc.recv(29+32).decode()
        messages.put(message)





def bruteforceFunc():
    global task
    global found
    global checked
    global stopThread
    global password
    global stopRun
    while True and not stopThread:
        while not task:
            pass
        # there is job to do
        taskList = str.split(task, ',')
        print(taskList)
        print('start decrypting')
        taskDict = {'start':str.split(taskList[0], ':')[1], 'stop':str.split(taskList[1], ':')[1], 'md5':str.split(taskList[2], ':')[1]}
        task = None
        # split into four tasks
        checkRange = splitTasks(taskDict)
        t1 = threading.Thread(target=decryptMD5, args=(taskDict['md5'], checkRange[0][0], checkRange[0][1]))
        t2 = threading.Thread(target=decryptMD5, args=(taskDict['md5'], checkRange[0][0], checkRange[0][1]))
        t3 = threading.Thread(target=decryptMD5, args=(taskDict['md5'], checkRange[0][0], checkRange[0][1]))
        t4 = threading.Thread(target=decryptMD5, args=(taskDict['md5'], checkRange[0][0], checkRange[0][1]))
        # run four threads
        t1.start()
        t2.start()
        t3.start()
        t4.start()
        while t1.is_alive() or t2.is_alive() or t3.is_alive() or t4.is_alive():
            if password:
                found = True
                stopThread = True
            if stopRun:
                stopThread = True
        checked = True
        # wait for password to appear, if appears stop threads
        # if doesnt appear wait till stop

def splitTasks(taskDict):
    # convert start stop to int
    start = convertStrToInt(taskDict['start'])
    stop = convertStrToInt(taskDict['stop'])
    # calc hefresh/4
    hefresh = (stop - start) / 4
    # add every time ^ -1
    checkRange = []
    for i in range(3):
        rng = [convertIntToStr(start), convertIntToStr(start+hefresh-1)]
        checkRange.append(rng)
        start += hefresh
    checkRange.append([convertIntToStr(start), convertIntToStr(stop)])
    return checkRange

def convertStrToInt(strToConvert):
    convertedInt = 0
    for i in range(len(strToConvert)):
        convertedInt += (ord(strToConvert[i]) - ord('a')) * (26**i)
    return convertedInt

def convertIntToStr(intToConvert):
    convertedStr = ''
    while intToConvert > 0:
        letter = intToConvert % 26
        letter += ord('a')
        letter = chr(int(letter))
        convertedStr = letter + convertedStr
        intToConvert /= 26
    return convertedStr





# main func
def decryptMD5(md5, start, stop):
    global password
    global stopThread
    check = convertStrToAsciiList(start)
    stop = convertStrToAsciiList(stop)
    while len(check) <= len(stop) and not stopThread:
        foundMatch = checkMatchingCombination(check, 0, md5, stop)
        if foundMatch:
            password = foundMatch
            break
        check.append(97)
        check = [97 for a in check]
    
# run through possible combinations and check if their md5 matches requested md5
def checkMatchingCombination(asciiList, index, md5, stopList): #get index zero, everytime index +1
    if index == len(asciiList):
        return compareToMD5(asciiList, md5)
    
    while asciiList[index] != 123:
        if asciiList == stopList:
            return False
        isMatch = checkMatchingCombination(list.copy(asciiList), index+1, md5, stopList)
        if isMatch:
            return isMatch
        if isMatch is False:
            return False
        if index != len(asciiList)-1:
            asciiList[index+1] = 97
        asciiList[index] += 1
    
    return
    
# convert string to list of ascii
def convertStrToAsciiList(strToConvert):
    asciiList = [ord(i) for i in strToConvert]
    return asciiList

# get md5 hash of string
def getStringHash(strToHash):
    hashObj = hashlib.md5()
    hashObj.update(strToHash.encode('utf-8'))
    hashHex = hashObj.hexdigest()
    return hashHex

# compare currently checked string to md5
def compareToMD5(asciiList, md5):
    strList = [chr(i) for i in asciiList]
    #print('compareToMD5 - str list: ' + str(strList))
    strToCompare = ''.join(strList)
    strHash = getStringHash(strToCompare)
    if strHash == md5:
        return strToCompare
    return






def main():
    # thread communication
    comThread = threading.Thread(target=communicationFunc)
    # thread bruteforce
    bfThread = threading.Thread(target=bruteforceFunc)
    
    comThread.start()
    bfThread.start()


if __name__ == '__main__':
    main()
