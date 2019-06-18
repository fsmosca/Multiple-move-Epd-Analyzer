set MT=1000
set HASH=256
set THREADS=1
set OUTPUT=2-moves.txt
set EPD=.\epd\2-moves.epd

:: MT is movetime in milliseconds

:: A. uci engine

:: (1) Example with depth limit and multipv
c:\python36\python.exe mea.py --engine ".\engines\Deuterium_v2019.1.36.50_x64_pop.exe" ^
--name "Deuterium v2019.1.36.50" --hash %HASH% --eoption "depth=8, multipv=3" ^
--rating 2800 --protocol uci --epd %EPD% --movetime %MT% ^
--output %OUTPUT% --log

:: (2) Example with single thread and other engine specific option
:: c:\python36\python.exe mea.py --engine "c:\chess\engines\stockfish\stockfish_10.exe" ^
:: --name "Stockfish 10" --hash %HASH% --threads 1 ^
:: --eoption "contempt=0" --rating 3400 --protocol uci --epd %EPD% ^
:: --movetime %MT% --output %OUTPUT% --log

:: (3) Example using mea.exe
:: mea.exe --engine ".\engines\Deuterium_v2019.1.36.50_x64_pop.exe" ^
:: --name "Deuterium v2019.1.36.50" --hash %HASH% --eoption "depth=8, multipv=3" ^
:: --rating 2800 --protocol uci --epd %EPD% --movetime %MT% ^
:: --output %OUTPUT% --log


::-----------------------------------------------------------------------------


:: B. winboard engine
:: --eoption is not supported

:: (1) Example when xboard engine supports st value command, use --stmode 1
:: mea.exe --engine "C:\chess\engines\Dirty_CUCUMBER\Dirty.exe -hash 256" ^
:: --name "Dirty CUCUMBER" --hash %HASH% --protocol xboard --protover 2 --stmode 1 ^
:: --rating 2797 --epd %EPD% --movetime %MT% --output %OUTPUT% --log


pause