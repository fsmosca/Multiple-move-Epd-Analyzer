# Multiple-move Epd Analyzer
Analyzes epd file having multiple solution moves with points and generates text and html output files.

### Sample output

Sample [html output](https://fsmosca.github.io/Multiple-move-Epd-Analyzer/).

![html-output](https://user-images.githubusercontent.com/22366935/129468957-13cbcd87-ddc5-4abc-87dc-b4add13a1f61.png)

### Command line
```
python mea.py --engine ".\engines\Deuterium_v2019.1.36.50_x64_pop.exe" ^
--name "Deuterium v2019.1.36.50" --hash 256 ^
--rating 2773 --protocol uci --epd Openings200-mea.epd --movetime 1000 ^
--output Openings200-mea.txt --log
```

### Dependent modules
* Python-chess <br>
https://github.com/niklasf/python-chess <br>
Converts uci move format to san move format

### Installation
#### Run using the source
* Python 3.7 and up  
  for mea v0.5 and up  
  https://www.python.org/downloads/  
* Python 3.6  
  for mea below 0.5
  
* Python-chess  
https://github.com/niklasf/python-chess  
pip install python-chess

* mea.py  
https://github.com/fsmosca/Multiple-move-Epd-Analyzer

#### Run using exe file
Just download the exe file in Release link

### Getting started
* Example command line  
Run uci engine at 1s per position.
```
python mea.py --engine ".\engines\Deuterium_v2019.1.36.50_x64_pop.exe" --name "Deuterium v2019.1.36.50" --epd ".\epd\openings200-mea.epd" --hash 256 --movetime 1000 --log
```

* Output files
1. log output file will be moved to log folder  
2. epd output file will be moved to epd_out folder  
3. html file

* Help
```
usage: mea.py [-h] -i EPD [-o OUTPUT] -e ENGINE [--eoption EOPTION] -n NAME [-t THREADS] [-m HASH] [-a MOVETIME] [-r RATING] [-p PROTOCOL] [-s {0,1}] [--stmode {0,1}] [--protover {1,2}] [--infinite] [--log] [--runenginefromcwd]

Analyzes epd file having multiple solution moves with points

optional arguments:
  -h, --help            show this help message and exit
  -i EPD, --epd EPD     input epd filename
  -o OUTPUT, --output OUTPUT
                        text output filename for result, default=mea_results.txt
  -e ENGINE, --engine ENGINE
                        engine filename
  --eoption EOPTION     uci engine option, --eoption "contempt=true, Futility Pruning=false, pawn value=120"
  -n NAME, --name NAME  engine name
  -t THREADS, --threads THREADS
                        Threads or cores to be used by the engine, default=1.
  -m HASH, --hash HASH  Hash in MB to be used by the engine, default=64.
  -a MOVETIME, --movetime MOVETIME
                        Analysis time in milliseconds, 1s = 1000ms, default=500
  -r RATING, --rating RATING
                        You may input a rating for this engine, this will be shown in the output file, default=2500
  -p PROTOCOL, --protocol PROTOCOL
                        engine protocol [uci/xboard], default=uci
  -s {0,1}, --san {0,1}
                        for xboard engine, set this to 1 if it will send a move in san format, default=0
  --stmode {0,1}        for xboard engines, set this to 0 if it does not support st command, default=1
  --protover {1,2}      for xboard engines, this is protocol version number, default=2
  --infinite            Run uci engine with go infinite
  --log                 Records engine and analyzer output to [engine name]_[movetime]_log.txt
  --runenginefromcwd    Run engine from mea folder

MEA v0.8.0
```

### Credits
* Python-chess <br>
https://github.com/niklasf/python-chess  
* Kai Laskos  
openings200.epd
* Sedat Canbaz  
OTSv4.epd  
https://sites.google.com/site/computerschess/ots-v4-ranking
* Tony Hedlund  
tony-pos.epd  
https://privat.bahnhof.se/wb432434/fentest.htm

