from PySide2 import QtCore
import subprocess, time, os, sys, signal

if hasattr(sys, 'frozen'):
    realpath = sys._MEIPASS
else:
    realpath = '/'.join(sys.argv[0].replace("\\", "/").split("/")[:-1])
    
common_params = ["--source", "winget", "--accept-source-agreements"]
    
#winget = os.path.join(os.path.join(realpath, "winget-cli"), "AppInstallerCLI.exe")
winget = os.path.join(os.path.join(realpath, "winget-cli"), "winget.exe")
#winget = "winget"

def searchForPackage(signal: QtCore.Signal, finishSignal: QtCore.Signal, noretry: bool = False) -> None:
    print(f"[   OK   ] Starting winget search, winget on {winget}...")
    p = subprocess.Popen([winget, "search", ""] + common_params, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, cwd=os.getcwd(), env=os.environ, shell=True)
    output = []
    counter = 0
    idSeparator = 0
    while p.poll() is None:
        line = p.stdout.readline()
        line = line.strip()
        if line:
            if(counter > 1):
                output.append(str(line, encoding='utf-8', errors="ignore"))
            else:
                l = str(line, encoding='utf-8', errors="ignore").replace("\x08-\x08\\\x08|\x08 \r","")
                l = l.split("\r")[-1]
                if("Id" in l):
                    idSeparator = len(l.split("Id")[0])
                    verSeparator = idSeparator+2
                    i=0
                    while l.split("Id")[1].split(" ")[i] == "":
                        verSeparator += 1
                        i += 1
                counter += 1
    if p.returncode != 0 and not noretry:
        time.sleep(1)
        print(p.returncode)
        searchForPackage(signal, finishSignal, noretry=True)
    else:
        counter = 0
        for element in output:
            try:
                element = bytes(element, "utf-8")
                export = (element[0:idSeparator], element[idSeparator:verSeparator], element[verSeparator:])
                signal.emit(str(export[0], "utf-8").strip(), str(export[1], "utf-8").strip(), str(export[2], "utf-8").split(" ")[0].strip(), "Winget")
            except Exception as e:
                try:
                    element = str(element, "utf-8")
                    signal.emit(element[0:idSeparator].strip(), element[idSeparator:verSeparator].strip(), element[verSeparator:].split(" ")[0].strip(), "Winget")
                except Exception as e:
                    print(type(e), str(e))
                except Exception as e:
                    print(e)
        print("[   OK   ] Winget search finished")
        finishSignal.emit("winget")

def searchForUpdates(signal: QtCore.Signal, finishSignal: QtCore.Signal, noretry: bool = False) -> None:
    print(f"[   OK   ] Starting winget search, winget on {winget}...")
    p = subprocess.Popen([winget, "upgrade"] + common_params[0:2], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, cwd=os.getcwd(), env=os.environ, shell=True)
    output = []
    counter = 0
    idSeparator = 0
    while p.poll() is None:
        line = p.stdout.readline()
        line = line.strip()
        if line:
            if(counter > 1):
                if not b"upgrades available" in line:
                    output.append(str(line, encoding='utf-8', errors="ignore"))
            else:
                l = str(line, encoding='utf-8', errors="ignore").replace("\x08-\x08\\\x08|\x08 \r","")
                l = l.split("\r")[-1]
                print(l)
                if("Id" in l):
                    idSeparator = len(l.split("Id")[0])
                    verSeparator = len(l.split("Version")[0])
                    newVerSeparator = len(l.split("Available")[0])
                counter += 1
    
    if p.returncode != 0 and not noretry:
        time.sleep(1)
        print(p.returncode)
        searchForUpdates(signal, finishSignal, noretry=True)
    else:
        counter = 0
        for element in output:
            try:
                element = bytes(element, "utf-8")
                export = (element[0:idSeparator], element[idSeparator:verSeparator], element[verSeparator:])
                signal.emit(str(export[0], "utf-8").strip(), str(export[1], "utf-8").strip(), str(export[2], "utf-8").split(" ")[0].strip(), "Winget")
            except Exception as e:
                try:
                    element = str(element, "utf-8")
                    signal.emit(element[0:idSeparator].strip(), element[idSeparator:verSeparator].strip(), element[verSeparator:newVerSeparator].split(" ")[0].strip(), element[newVerSeparator:].split(" ")[0].strip(), "Winget")
                except Exception as e:
                    print(type(e), str(e))
                except Exception as e:
                    print(e)
        print("[   OK   ] Winget search finished")
        finishSignal.emit("winget")

def searchForInstalledPackage(signal: QtCore.Signal, finishSignal: QtCore.Signal) -> None:
    print(f"[   OK   ] Starting winget search, winget on {winget}...")
    p = subprocess.Popen([winget, "uninstall"] + common_params, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, cwd=os.getcwd(), env=os.environ, shell=True)
    output = []
    counter = 0
    idSeparator = 0
    while p.poll() is None:
        line = p.stdout.readline()
        line = line.strip()
        if line:
            if(counter > 2 and not b"---" in line):
                output.append(str(line, encoding='utf-8', errors="ignore"))
            else:
                l = str(line, encoding='utf-8', errors="ignore").replace("\x08-\x08\\\x08|\x08 \r","")
                l = l.split("\r")[-1]
                if("Id" in l):
                    idSeparator = len(l.split("Id")[0])
                counter += 1
    counter = 0
    emptyStr = ""
    wingetName = "Winget"
    for element in output:
        try:
            element = bytes(element, "utf-8")
            export = (element[0:idSeparator], element[idSeparator:])#verSeparator], element[verSeparator:])
            signal.emit(str(export[0], "utf-8").strip(), str(export[1], "utf-8").strip(), emptyStr, wingetName)
        except Exception as e:
            try:
                element = str(element, "utf-8")
                signal.emit(element[0:idSeparator].strip(), element[idSeparator:].strip(), emptyStr, wingetName)
            except Exception as e:
                print(type(e), str(e))
            except Exception as e:
                print(e)
    print("[   OK   ] Winget uninstallable packages search finished")
    finishSignal.emit("winget")

def getInfo(signal: QtCore.Signal, title: str, id: str, goodTitle: bool) -> None:
    if not(goodTitle):
        print(f"[   OK   ] Acquiring title for id \"{title}\"")
        p = subprocess.Popen([winget, "search", f"{title}"]+common_params, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, cwd=os.getcwd(), env=os.environ, shell=True)
        output = []
        while p.poll() is None:
            line = p.stdout.readline()
            line = line.strip()
            if line and not b"---" in line:
                output.append(str(line, encoding='utf-8', errors="ignore"))
        try:
            title = output[-1][0:output[0].split("\r")[-1].index("Id")].strip()
        except:
            pass
    print(f"[   OK   ] Starting get info for title {title}")
    p = subprocess.Popen([winget, "show", f"{title}"]+common_params, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, cwd=os.getcwd(), env=os.environ, shell=True)
    output = []
    appInfo = {
        "title": title,
        "id": id,
        "publisher": "Unknown",
        "author": "Unknown",
        "description": "Unknown",
        "homepage": "Unknown",
        "license": "Unknown",
        "license-url": "Unknown",
        "installer-sha256": "Unknown",
        "installer-url": "Unknown",
        "installer-type": "Unknown",
        "manifest": "Unknown",
        "versions": [],
    }
    while p.poll() is None:
        line = p.stdout.readline()
        line = line.strip()
        if line:
            output.append(str(line, encoding='utf-8', errors="ignore"))
    for line in output:
        if("Publisher:" in line):
            appInfo["publisher"] = line.replace("Publisher:", "").strip()
        elif("Description:" in line):
            appInfo["description"] = line.replace("Description:", "").strip()
        elif("Author:" in line):
            appInfo["author"] = line.replace("Author:", "").strip()
        elif("Publisher:" in line):
            appInfo["publisher"] = line.replace("Publisher:", "").strip()
        elif("Homepage:" in line):
            appInfo["homepage"] = line.replace("Homepage:", "").strip()
        elif("License:" in line):
            appInfo["license"] = line.replace("License:", "").strip()
        elif("License Url:" in line):
            appInfo["license-url"] = line.replace("License Url:", "").strip()
        elif("SHA256:" in line):
            appInfo["installer-sha256"] = line.replace("SHA256:", "").strip()
        elif("Download Url:" in line):
            appInfo["installer-url"] = line.replace("Download Url:", "").strip()
        elif("Type:" in line):
            appInfo["installer-type"] = line.replace("Type:", "").strip()
    print(f"[   OK   ] Loading versions for {title}")
    p = subprocess.Popen([winget, "show", f"{title}", "--versions"]+common_params, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, cwd=os.getcwd(), env=os.environ, shell=True)
    output = []
    counter = 0
    while p.poll() is None:
        line = p.stdout.readline()
        line = line.strip()
        if line:
            if(counter > 2):
                output.append(str(line, encoding='utf-8', errors="ignore"))
            else:
                counter += 1
    appInfo["versions"] = output
    signal.emit(appInfo)
    
def installAssistant(p: subprocess.Popen, closeAndInform: QtCore.Signal, infoSignal: QtCore.Signal, counterSignal: QtCore.Signal) -> None:
    print(f"[   OK   ] winget installer assistant thread started for process {p}")
    outputCode = 0
    counter = 0
    output = ""
    while p.poll() is None:
        line = p.stdout.readline()
        line = line.strip()
        line = str(line, encoding='utf-8', errors="ignore").strip()
        if line:
            infoSignal.emit(line)
            counter += 1
            counterSignal.emit(counter)
            output += line+"\n"
    p.wait()
    outputCode = p.returncode
    closeAndInform.emit(outputCode, output)
 
def uninstallAssistant(p: subprocess.Popen, closeAndInform: QtCore.Signal, infoSignal: QtCore.Signal, counterSignal: QtCore.Signal) -> None:
    print(f"[   OK   ] winget installer assistant thread started for process {p}")
    outputCode = 0
    counter = 0
    output = ""
    while p.poll() is None:
        line = p.stdout.readline()
        line = line.strip()
        line = str(line, encoding='utf-8', errors="ignore").strip()
        if line:
            infoSignal.emit(line)
            counter += 1
            counterSignal.emit(counter)
            output += line+"\n"
    p.wait()
    outputCode = p.returncode
    closeAndInform.emit(outputCode, output)



if(__name__=="__main__"):
    import __init__
