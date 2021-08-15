set MT=1000
set HASH=256
set THREADS=1
set OUTPUT=Openings200-mea.txt
set EPD=.\epd\Openings200-mea.epd

:: MT is movetime in milliseconds

mea.exe --help >help.txt

:: A. uci engine

python mea.py --engine ".\engines\Deuterium_v2019.1.36.50_x64_pop.exe" ^
--name "Deuterium v2019.1.36.50" --hash %HASH% ^
--rating 2773 --protocol uci --epd %EPD% --movetime %MT% ^
--output %OUTPUT% --log


python mea.py --engine ".\engines\Deuterium_v2019.2.37.73_64bit_pop.exe" ^
--name "Deuterium v2019.2.37.73" --hash %HASH% ^
--rating 2824 --protocol uci --epd %EPD% --movetime %MT% ^
--output %OUTPUT% --log

goto end


:: (1) Example with depth limit and multipv
python mea.py --engine ".\engines\Deuterium_v2019.1.36.50_x64_pop.exe" ^
--hash %HASH% --eoption "depth=12, multipv=3" ^
--rating 2850 --protocol uci --epd %EPD% --movetime %MT% ^
--output %OUTPUT% --log


:: (2) Example with single thread and other engine specific option
:: mea.exe --engine "C:\chess\engines\stockfish\stockfish_10.exe" ^
:: --name "Stockfish 10" --hash %HASH% --threads 1 ^
:: --eoption "contempt=0" --rating 3450 --protocol uci --epd %EPD% ^
:: --movetime %MT% --output %OUTPUT% --log

:: mea.exe --engine "C:\chess\engines\wasp_360\Wasp360-x64.exe" ^
:: --name "Wasp 3.60" --eoption "threads=1, hash=256" --rating 2930 ^
:: --protocol uci --epd %EPD% --movetime %MT% --output %OUTPUT% --log

:: mea.exe --engine "C:\chess\engines\smt198\SmarThink_v198_x64_SSE3_standalone.exe" ^
:: --name "SmarThink 1.98" --eoption "threads=1, hash=256" --rating 2900 ^
:: --protocol uci --epd %EPD% --movetime %MT% --output %OUTPUT% --log

:: mea.exe --engine "C:\chess\engines\LCZERO\lc0-v0.21.2-windows-blas\Lc0.exe" ^
:: --name "Lc0 v0.21.2 w11258-112x9" --threads %THREADS% ^
:: --eoption "smartpruningfactor=0, ramlimitmb=512, weightsfile=C:\chess\engines\LCZERO\id\11258-112x9-se.pb.gz" ^
:: --protocol uci --rating 2800 --epd %EPD% --movetime %MT% --output %OUTPUT% --log


::-----------------------------------------------------------------------------


:: B. winboard engine
:: --eoption is not supported

:: (1) Example when xboard engine supports st value command, use --stmode 1
:: mea.exe --engine "C:\chess\engines\Dirty_CUCUMBER\Dirty.exe -hash 256" ^
:: --name "Dirty CUCUMBER" --hash %HASH% --protocol xboard --protover 2 --stmode 1 ^
:: --rating 2800 --epd %EPD% --movetime %MT% --output %OUTPUT% --log

:end

pause