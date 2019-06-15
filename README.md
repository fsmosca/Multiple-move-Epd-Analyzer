# Multiple-move Epd Analyzer
Analyzes epd file having multiple solution moves with points

### Dependent modules
* Python-chess <br>
https://github.com/niklasf/python-chess <br>
Converts uci move format to san move format
* Py-cpuinfo <br>
https://github.com/workhorsy/py-cpuinfo <br>
Get processor info, brand and number of cores

### Installation
* Python 2.7.16 <br>
https://www.python.org/downloads/release/python-2716/ <br>
* Python-chess<br>
https://github.com/niklasf/python-chess <br>
pip install python-chess
* Py-cpuinfo <br>
https://github.com/workhorsy/py-cpuinfo <br>
python -m pip install -U py-cpuinfo
* mea.py <br>
https://github.com/fsmosca/Multiple-move-Epd-Analyzer

### Getting started
* c:\python27\python.exe mea.py --[options] [option value] <br>
```
usage: mea.py [-h] -i EPD [-o OUTPUT] -e ENGINE [--eoption EOPTION] -n NAME
              [-t THREADS] [-m HASH] [-a MOVETIME] [-r RATING] [-p PROTOCOL]
              [-s {0,1}] [--stmode {0,1}] [--protover {1,2}] [--log]

Analyzes epd file having multiple solution moves with points

optional arguments:
  -h, --help            show this help message and exit
  -i EPD, --epd EPD     input epd filename
  -o OUTPUT, --output OUTPUT
                        text output filename for result,
                        default=mea_results.txt
  -e ENGINE, --engine ENGINE
                        engine filename
  --eoption EOPTION     uci engine option, --eoption "contempt=true, Futility
                        Pruning=false, pawn value=120"
  -n NAME, --name NAME  engine name
  -t THREADS, --threads THREADS
                        Threads or cores to be used by the engine, default=1.
  -m HASH, --hash HASH  Hash in MB to be used by the engine, default=64.
  -a MOVETIME, --movetime MOVETIME
                        Analysis time in milliseconds, 1s = 1000ms,
                        default=500
  -r RATING, --rating RATING
                        You may input a rating for this engine, this will be
                        shown in the output file, default=2500
  -p PROTOCOL, --protocol PROTOCOL
                        engine protocol [uci/xboard], default=uci
  -s {0,1}, --san {0,1}
                        for xboard engine, set this to 1 if it will send a
                        move in san format, default=0
  --stmode {0,1}        for xboard engines, set this to 0 if it does not
                        support st command, default=1
  --protover {1,2}      for xboard engines, this is protocol version number,
                        default=2
  --log                 Records engine and analyzer output to [engine
                        name]_[movetime]_log.txt

MEA v0.3
```

### Credits
* Python-chess <br>
https://github.com/niklasf/python-chess <br>
* Py-cpuinfo <br>
https://github.com/workhorsy/py-cpuinfo <br>
