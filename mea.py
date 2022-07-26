"""
A. Program name
MEA - Multiple move EPD Analyzer

B. Program description
Analyzes epd file having multiple solution moves with points
"""


import os
import subprocess
from pathlib import Path
import logging
import time
import re
import csv
import argparse

import chess


__version__ = '1.0'
__credits__ = ['majkelnowaq']


APP_NAME = 'MEA'
APP_DESC = 'Analyzes epd file having multiple solution moves with points'
APP_NAME_VERSION = APP_NAME + ' v' + __version__


# Create logger
logger = logging.getLogger('mea')
logger.setLevel(logging.DEBUG)


def move_file(dirname, filename):
    """ Move filename to dirname, create dirname if it does not exists """
    cwd = Path.cwd()
    
    dir_path = Path(cwd, dirname)
    if not dir_path.exists():
        dir_path.mkdir()
        
    # If we successfully created the dir we will move our file there
    if dir_path.exists():
        file_path = Path(cwd, filename)

        # If log file exists
        if file_path.exists():
            new_file_path = Path(dir_path, filename)

            # Move/replace file to new dir
            file_path.replace(new_file_path)
            
            if new_file_path.exists():
                print('File {} was sucessfully moved to {}.'.format(filename, dir_path))

def delete_file(fn):
    """ Delete file if it exist """
    if os.path.isfile(fn):
        os.remove(fn)


def sort_key_top1(item):
    """ Sort by top1 score """
    return item[2]


def sort_key_score(item):
    """ Sort by score """
    return item[5]


def csv_to_html(csvfn, htmlfn, epdfn):
    """ Creates table in html format from csv file """
    # Get epd filename alone, not including path
    epd_fn_only = epdfn.split('\\')
    varlen = len(epd_fn_only)
    if varlen > 0:
        epd_fn_name = epd_fn_only[varlen-1]
    else:
        epd_fn_name = epdfn
    
    # Open the CSV file for reading
    reader = csv.reader(open(csvfn))

    # Create the HTML file for output
    htmlfile = open(htmlfn, 'w')

    # initialize rownum variable
    rownum = 0

    htmlfile.write('<!DOCTYPE html>\n')
    htmlfile.write('<head>\n')
    htmlfile.write('<style>\n')
    htmlfile.write('body{margin-top:0px;margin-left:128px;margin-right:128px;}\n')
    htmlfile.write('table {width:100%;}\n')
    htmlfile.write('table, th, td {border: 1px solid black;border-collapse: ' + 
        'collapse;collapse;font-family: "Calibri", serif;font-size: 16px;}\n')
    htmlfile.write('th, td {padding: 5px;text-align: left;}\n')
    htmlfile.write('table#t01 tr:nth-child(even) {background-color: #eee;}\n')
    htmlfile.write('table#t01 tr:nth-child(odd) {background-color:#fff;}\n')
    htmlfile.write('table#t01 th {background-color: black;color: white;}\n')
    htmlfile.write('</style>\n')
    htmlfile.write('</head>\n')
    htmlfile.write('<body>\n')

    htmlfile.write('<h3>%s</h3>\n' %(APP_NAME))

    htmlfile.write('<strong>A. EPD test set:</strong><br>\n')
    htmlfile.write('Filename: %s<br><br>\n' %(epd_fn_name))

    # write <table> tag
    htmlfile.write('<table id="t01">')

    # generate table contents

    for row in reader: # Read a single row from the CSV file
        # write header row. assumes first row in csv contains header
        if rownum == 0:
            htmlfile.write('<tr>') # write <tr> tag
            for column in row:
                htmlfile.write('<th>' + column + '</th>')
            htmlfile.write('</tr>')

        #write all other rows
        else:
            htmlfile.write('<tr>')
            for column in row:
                htmlfile.write('<td>' + column + '</td>')
            htmlfile.write('</tr>')

        #increment row count
        rownum += 1

    # write </table> tag
    htmlfile.write('</table>\n')

    htmlfile.write('</body>\n')
    htmlfile.write('</html>\n')


class Analyze():     
    def __init__(self, engine, fen_list, max_epd_cnt, movetime, num_threads,
                 num_hash, proto, name, san, stmode, protover, epd_output_fn,
                 multipv, eoption, input_epd_name, infinite, runenginefromcwd):
        self.engine = engine
        self.fen_list = fen_list # [fen, solutions, id]
        self.max_epd_cnt = max_epd_cnt
        self.movetime = movetime
        self.num_threads = num_threads
        self.num_hash = num_hash
        self.num_pos_tried = 0
        self.best_cnt = 0
        self.total_score = 0        
        self.max_score = 0
        self.stop_time_margin_ms = max(10, min(100, self.movetime//4))
        self.proto = proto
        self.name = name
        self.san = san
        self.stmode = stmode
        self.protover = protover  # 1 or 2
        self.eoption = eoption
        self.epd_output_fn = epd_output_fn
        self.multipv = multipv
        self.input_epd_name = input_epd_name
        self.depth = -1
        self.infinite = infinite
        self.runenginefromcwd = runenginefromcwd

    def run(self):
        """ Run engine to analyze epd """
        if self.proto == 'xboard':
            self.run_xb_engine()
        else:
            self.run_uci_engine()
            
    def update_score(self, fen_line, movesan):
        """ Update score of the engine """
        bests = fen_line # Nd2=10, h3=7, Be2=6
        best_list = bests.split(',')
        
        top_move_cnt = 0                    
        this_move_score = 0
        
        # Loop thru the solution moves ['Nd2=10', 'h3=7', 'Be2=6']
        for n in best_list:
            top_move_cnt += 1
            # Deal with 2 equal symbols, b1=Q=77
            if n.count('=') == 2:
                m = n.split('=')[0] + '=' +  n.split('=')[1] # Get move
                m = m.strip()
                move_score = int(n.split('=')[2])  # Get score
            else:
                m = n.split('=')[0]  # Get move
                m = m.strip()
                move_score = int(n.split('=')[1])  # Get score
                
            # Assume that the first solution move has the highest score
            if top_move_cnt == 1:
                self.max_score += move_score
                
            # Check if engne bm is the same to one of the solution moves
            if m == movesan:
                this_move_score = move_score
                if top_move_cnt == 1:
                    self.best_cnt += 1
                    logger.info('Top 1 move!!')
                self.total_score += move_score
                break
            
        # Get pct of score after thie epd so far
        logger.info('Score for this test: %d' % this_move_score)
        pct = float(self.total_score)/self.max_score if self.max_score > 0 else 0.0 
        logger.info('Total Score update: %d / %d (%0.3f)'\
                       % (self.total_score, self.max_score, pct))
            
    def mate_distance_to_value(self, d):
        """ Returns value in cp given distance to mate """
        value = 0
        if d < 0:
            value = -2*d - 32000
        elif d > 0:
            value = 32000 - 2*d + 1

        return value

    def get_result(self):
        return [self.name, self.best_cnt, self.total_score,
                self.max_score, self.num_pos_tried]
        
    def run_uci_engine(self):
        """ Start engine """
        logger.info('Run engine %s' % self.name)
        
        # Run from engine's folder by default and not from mea's folder
        folder = Path(self.engine).parents[0] if not self.runenginefromcwd else None
        
        # Python 3.7
        p = subprocess.Popen(self.engine, bufsize=1, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             universal_newlines=True, cwd=folder)
        
        p.stdin.write('uci\n')
        logger.debug('>> uci')
        
        for eline in iter(p.stdout.readline, ''):
            line = eline.strip()
            logger.debug('<< %s' % line)
            if 'uciok' in line:
                break

        # Threads
        p.stdin.write('setoption name threads value %d\n' % self.num_threads)
        logger.debug('>> setoption name threads value %d' % self.num_threads)

        # Hash in mb
        p.stdin.write('setoption name Hash value %d\n' % self.num_hash)
        logger.debug('>> setoption name Hash value %d' % self.num_hash)
        
        # Other options
        # 'Futility Pruning=true, lmr=false, contempt=false'
        if self.eoption is not None:
            opt_list = self.eoption.split(',')
            logger.info('eoption: %s' % opt_list)
            for o in opt_list:
                opt = o.strip()
                name = opt.split('=')[0].strip()
                value = opt.split('=')[1].strip()

                # Send go depth value when depth is in --eoption
                if name.lower() == 'depth':
                    self.depth = int(value)
                    continue
                
                # Set it
                p.stdin.write('setoption name %s value %s\n' % (name, value))
                logger.debug('>> setoption name %s value %s' % (name, value))
        
        # Prepare engine
        p.stdin.write('isready\n')
        logger.debug('>> isready')
                
        for eline in iter(p.stdout.readline, ''):
            aa = eline.strip()
            if 'readyok' in aa:
                logger.debug('<< readyok')
                break

        line_cnt = 0
        t1 = time.perf_counter()        

        for fen_line in self.fen_list:
            logger.info('\n')
            logger.info('Pos %d' % (line_cnt+1))
            logger.info('EPD: %s' % fen_line[3])
            logger.info('id %s' % fen_line[2])
            logger.info('FEN: %s' % fen_line[0])
            logger.info('Solutions: %s' % fen_line[1])
            
            search_info = {}
                    
            line_cnt += 1

            # Console progress
            print('epd %d / %d \r' %(line_cnt, self.max_epd_cnt)),
            
            depth_info = 0
            score_cp_info = -32000
            fen = fen_line[0]
            movesan = None
            
            p.stdin.write('ucinewgame\n')
            logger.debug('>> ucinewgame')
            
            # Prepare engine
            p.stdin.write('isready\n')
            logger.debug('>> isready')
                    
            for eline in iter(p.stdout.readline, ''):
                if 'readyok' in eline:
                    logger.debug('<< readyok')
                    break

            p.stdin.write('position fen ' + fen + '\n')
            logger.debug('>> position fen ' + fen)
            
            go_start = time.perf_counter()
            if self.depth > 0:
                if self.movetime <= 0:
                    p.stdin.write('go depth %d\n' % (self.depth))
                    logger.debug('>> go depth %d' % (self.depth))
                else:
                    p.stdin.write('go movetime %d depth %d\n' % (self.movetime, self.depth))
                    logger.debug('>> go movetime %d depth %d' % (self.movetime, self.depth))
            # Send go infinite for engines that does not support movetime and/or depth properly
            elif self.infinite:
                p.stdin.write('go infinite\n')
                logger.debug('>> go infinite')
            else:
                p.stdin.write('go movetime %d\n' % (self.movetime))
                logger.debug('>> go movetime %d' % (self.movetime))

            stop_sent = False
            max_depth = 1

            # Parse engine output
            for eline in iter(p.stdout.readline, ''):
                line = eline.strip()
                
                if ('depth ' in line and ' pv ' in line \
                    and not 'upperbound' in line \
                    and not 'lowerbound' in line) or 'bestmove' in line:
                    logger.debug('<< %s' % line)

                if self.multipv >= 2:
                    if ('score' in line and 'depth' in line and 'pv' in line
                            and not 'upperbound' in line
                            and not 'lowerbound' in line
                            and 'multipv' in line):
                        if 'score mate' in line:
                            distance_to_mate = int(line.split('mate')[1].split()[0].strip())
                            score_cp_info = self.mate_distance_to_value(distance_to_mate)
                        elif 'cp' in line:
                            score_cp_info = int(line.split('cp')[1].split()[0].strip())
                            
                        depth_info = int(line.split('depth')[1].split()[0])
                        mpv_info = int(line.split('multipv')[1].split()[0])
                        key = f'd{depth_info}_mpv{mpv_info}'

                        pv_info_first_move = line.split(' pv')[1].strip().split()[0]
                        tmp_board = chess.Board(fen)
                        
                        # Convert move from uci to san move format
                        pv_move_san = tmp_board.san(chess.Move.from_uci(pv_info_first_move))
                        
                        dict_value = {key: {'score': score_cp_info, 'depth': depth_info, 'bm': pv_move_san}}
                        search_info.update(dict_value)
                        max_depth = max(depth_info, max_depth)
                                
                elif 'depth' in line or 'score' in line:                    
                    # Get depth, assume depth first before seldepth
                    if 'depth' in line:
                        depth_info = int(line.split('depth')[1].split()[0])
                        max_depth = max(depth_info, max_depth)
                    
                    # Get score
                    if 'score' in line:
                        if 'score mate' in line:
                            distance_to_mate = int(line.split('mate')[1].split()[0].strip())
                            score_cp_info = self.mate_distance_to_value(distance_to_mate)
                        elif 'cp' in line:
                            score_cp_info = int(line.split('cp')[1].split()[0].strip())

                if 'bestmove' in line:
                    self.num_pos_tried += 1
                    bm = line.split()[1]
                    bm = bm.lower()

                    # Convert uci bestmove to san bestmove
                    tmp_board = chess.Board(fen)
                    movesan = tmp_board.san(chess.Move.from_uci(bm)) 
                    
                    logger.info('elapsed(ms) since go: {:0.0f}'.format(
                            (time.perf_counter() - go_start) * 1000))
                    logger.info('bestmove: {}'.format(movesan))
                    
                    self.update_score(fen_line[1], movesan)
                    break
                
                tdiff = (time.perf_counter() - go_start) * 1000

                # Send stop early if we re using go infinite
                if not stop_sent and self.infinite and tdiff > 2*self.movetime//3:
                    stop_sent = True
                    p.stdin.write('stop\n')
                    logger.debug('>> stop')

                # There are engines that does not follow movetime so we stop it
                if not stop_sent and tdiff - self.stop_time_margin_ms >= self.movetime:
                    stop_sent = True
                    p.stdin.write('stop\n')
                    logger.debug('>> stop')

            # Clean mpv result, save the last depth with complete mpv as
            # there are engines that do not complete the mpv at certain depth.
            fdata = []
            if self.multipv >= 2:
                fdata = get_mpv_data(search_info, max_depth)
                    
            epd = ' '.join(fen_line[0].split()[0:4])
            
            # Debug
            if self.multipv >= 2:
                for k, v in search_info.items():
                    logger.info('multipv {} = {}'.format(k, v))
            
            # Save epd with ce and acd
            # (1) Multipv is 1
            if self.multipv <= 1:
                with open(self.epd_output_fn, 'a') as h:
                    h.write('%s bm %s; ce %d; acd %d;\n' % (
                            epd, movesan, score_cp_info, depth_info))
                logger.info('%s bm %s; ce %d; acd %d;' % (epd, movesan,
                                                score_cp_info, depth_info))
            else:
                for i, v in enumerate(fdata):
                    id_operand = self.input_epd_name + ' pos ' + str(line_cnt) + ' MultiPV=' + str(i+1)
                    with open(self.epd_output_fn, 'a') as h:
                        h.write('%s id \"%s\"; bm %s; ce %d; acd %d;\n' % (
                                epd, id_operand, v[i+1]['bm'], v[i+1]['score'],
                                v[i+1]['depth']))
                    logger.info('%s id \"%s\"; bm %s; ce %d; acd %d;' % (
                            epd, id_operand, v[i+1]['bm'], v[i+1]['score'],
                            v[i+1]['depth']))

        # Quit engine when all fen are analyzed
        p.stdin.write('quit\n')
        logger.debug('>> quit')
        
        # Terminate engine process when engine does not quit after quit command        
        try:
            p.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            logger.warning('Engine is terminated by kill()')
            p.kill()
            p.communicate()

        t2 = time.perf_counter()

        # Check analysis time anomalies
        expectedMaxTime = self.movetime * self.max_epd_cnt  # ms
        ActualElapsedTime = (t2 - t1) * 1000  # ms
        timeMarginPerPos = max(50, min(200, self.movetime//4))  # ms
        timeMargin = self.max_epd_cnt * timeMarginPerPos  # ms
        
        if self.depth <= -1:
            if (ActualElapsedTime <= expectedMaxTime + timeMargin) and\
                    ActualElapsedTime >= expectedMaxTime - timeMargin:
                logger.info('Time allocation  : GOOD!!')
                logger.info('at <= et + mt and at >= et - mt')
                print('Time allocation  : GOOD!!')
                print('at <= et + mt and at >= et - mt')
            elif ActualElapsedTime > expectedMaxTime + timeMargin:
                logger.info('Time allocation  : BAD!! spending more time')
                logger.info('ActualTime > ExpectedTime + MarginTime')
                print('Time allocation  : BAD!! spending more time')
                print('at > et + mt')
            else:
                logger.info('Time allocation  : BAD!! spending less time')
                logger.info('at < et - mt')
                print('Time allocation  : BAD!! spending less time')
                print('at < et - mt')

        logger.info('ExpectedTime     : %0.1fs' %(float(expectedMaxTime)/1000))
        logger.info('ActualTime       : %0.1fs' %(float(ActualElapsedTime)/1000))
        logger.info('MarginTime/pos   : %0.1fs' %(float(timeMarginPerPos)/1000))
        logger.info('MarginTime       : %0.1fs' %(float(timeMargin)/1000))
        
        print('ExpectedTime     : %0.1fs' %(float(expectedMaxTime)/1000))
        print('ActualTime       : %0.1fs' %(float(ActualElapsedTime)/1000))
        print('MarginTime/pos   : %0.1fs' %(float(timeMarginPerPos)/1000))
        print('MarginTime       : %0.1fs' %(float(timeMargin)/1000))

    def run_xb_engine(self):
        """ Start engine """
        logger.info('Run engine %s' % self.name)
        
        folder = Path(self.engine).parents[0] if not self.runenginefromcwd else None
        
        # Python 3.7
        p = subprocess.Popen(self.engine, bufsize=1, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             universal_newlines=True, cwd=folder)
        
        p.stdin.write('xboard\n')
        logger.debug('>> xboard')

        # Wait for done=1, applies for protover 2 only
        if self.protover == 2:
            p.stdin.write('protover 2\n')
            logger.debug('>> protover 2')

            for eline in iter(p.stdout.readline, ''):
                line = eline.strip()
                logger.debug('<< %s' % line)
                if 'done=1' in line:                    
                    break

        logger.debug('>> post')
        p.stdin.write('post\n')

        p.stdin.write('new\n')
        logger.debug('>> new')

        p.stdin.write('hard\n')
        logger.debug('>> hard')

        p.stdin.write('easy\n')
        logger.debug('>> easy')

        line_cnt = 0
        t1 = time.perf_counter()

        for fen_line in self.fen_list:
            logger.info('\n')
            logger.info('Pos %d' %(line_cnt+1))
            logger.info('EPD: %s' % fen_line[3])
            logger.info('id %s' %(fen_line[2]))
            logger.info('FEN: %s' %(fen_line[0]))
            logger.info('Solutions: %s' %(fen_line[1]))
                    
            line_cnt += 1

            # Console progress
            print('epd %d / %d \r' %(line_cnt, self.max_epd_cnt)),
            
            # depth = 0
            fen = fen_line[0]
            
            p.stdin.write('new\n')
            logger.debug('>> new')

            p.stdin.write('force\n')
            logger.debug('>> force')
            
            p.stdin.write('setboard %s\n' % fen)
            logger.debug('>> setboard %s' % fen)

            # Use st
            if self.stmode:
                if self.movetime < 1000:
                    p.stdin.write('st %0.1f\n' % (self.movetime/1000.0))
                    logger.debug('>> st %0.1f' % (self.movetime/1000.0))
                else:
                    p.stdin.write('st %0.0f\n' % (self.movetime/1000.0))
                    logger.debug('>> st %0.0f' % (self.movetime/1000.0))
            # Use level
            else:
                period = 40
                tpm_ms = self.movetime  # ms
                tpm_s = period * tpm_ms/1000  # sec
                m, s = divmod(tpm_s, 60)
                if s == 0:
                    p.stdin.write('level %d %d 0\n' % (period, m))
                    logger.debug('>> level %d %d 0' % (period, m))
                    
                    p.stdin.write('time %d\n' % (period*tpm_ms/10))  # in centisec
                    logger.debug('>> time %d' % (period*tpm_ms/10))
                else:
                    # EXchess does not like m:n notation for min:sec in level
                    if 'exchess' in self.name.lower():
                        p.stdin.write('level %d %d 0\n' % (period, max(1, m)))
                        logger.debug('>> level %d %d 0' % (period, max(1, m)))                    
                        p.stdin.write('time %d\n' % (period*tpm_ms/10))
                        logger.debug('>> time %d' % (period*tpm_ms/10))
                    else:
                        p.stdin.write('level %d %d:%d 0\n' % (period, m, s))
                        logger.debug('>> level %d %d:%d 0' % (period, m, s))
                        p.stdin.write('time %d\n' % (period*tpm_ms/10))
                        logger.debug('>> time %d' % (period*tpm_ms/10))
            
            go_start = time.perf_counter()
            p.stdin.write('go\n')
            logger.debug('>> go')

            # Parse engine output
            for eline in iter(p.stdout.readline, ''):
                line = eline.strip()
                logger.debug('<< %s' % (line))
                if 'move' in line and len(line.split()) == 2:
                    self.num_pos_tried += 1
                    bm = line.split()[1]
                    bm = bm.strip()

                    if self.san:
                        movesan = bm
                    else:
                        # Convert uci bestmove to san bestmove
                        tmp_board = chess.Board(fen)
                        movesan = tmp_board.san(chess.Move.from_uci(bm))
                    
                    logger.info('elapsed(ms) since go: {:0.0f}'.format(
                            (time.perf_counter() - go_start) * 1000))
                    logger.info('bestmove: {}'.format(movesan))

                    self.update_score(fen_line[1], movesan)
                    break
                
            # (1) Multipv is 1
            if self.multipv == 1:
                epd = ' '.join(fen.split()[0:4]).strip()
                with open(self.epd_output_fn, 'a') as h:
                    h.write('%s bm %s;\n' % (epd, movesan))

        # Quit engine when all fen are analyzed
        p.stdin.write('quit\n')
        logger.debug('>> quit')
        
        try:
            p.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            logger.warning('Engine is terminated by kill()')
            p.kill()
            p.communicate()

        t2 = time.perf_counter()

        # Check analysis time anomalies
        expectedMaxTime = self.movetime * self.max_epd_cnt  # ms
        ActualElapsedTime = (t2 - t1) * 1000  # ms
        timeMarginPerPos = max(50, min(200, self.movetime//4))  # ms
        timeMargin = self.max_epd_cnt * timeMarginPerPos  # ms
        
        # winboard/xboard engine        
        if (ActualElapsedTime <= expectedMaxTime + timeMargin) and\
                ActualElapsedTime >= expectedMaxTime - timeMargin:
            logger.info('Time allocation  : GOOD!!')
            print('Time allocation  : GOOD!!')
        elif ActualElapsedTime > expectedMaxTime + timeMargin:
            logger.info('Time allocation  : BAD!! spending more time')
            print('Time allocation  : BAD!! spending more time')
        else:
            logger.info('Time allocation  : BAD!! spending less time')
            print('Time allocation  : BAD!! spending less time')

        logger.info('ExpectedTime     : %0.1fs' %(float(expectedMaxTime)/1000))
        logger.info('ActualTime       : %0.1fs' %(float(ActualElapsedTime)/1000))
        logger.info('TimeMargin/pos   : %0.1fs' %(float(timeMarginPerPos)/1000))
        logger.info('TimeMarginTotal  : %0.1fs' %(float(timeMargin)/1000))
        
        print('ExpectedTime     : %0.1fs' %(float(expectedMaxTime)/1000))
        print('ActualTime       : %0.1fs' %(float(ActualElapsedTime)/1000))
        print('TimeMargin/pos   : %0.1fs' %(float(timeMarginPerPos)/1000))
        print('TimeMarginTotal  : %0.1fs' %(float(timeMargin)/1000))


def get_mpv_data(search_info, max_depth):
    """Clean multipv search data.
    """
    # Get the number of mpv at depth 1 or next depth.
    d1_cnt = 0
    for i in range(1, 100):
        if d1_cnt > 0:
            break
        for k, v in search_info.items():
            if f'd{i}_mpv' in k:
                d1_cnt += 1
    # Find the last depth with complete mpv.
    iscut, depth_complete, last_i = False, 1, 1
    for i in range(1, max_depth+1):
        sk = f'd{i}_mpv'
        cnt = 0
        last_i = i
        for k, v in search_info.items():
            if sk in k:
                cnt += 1
        if cnt < d1_cnt and cnt != 0:
            # This is not a complete mpv.
            depth_complete = i-1
            iscut = True
            break
    if not iscut:
        # All depth have complete mpv.
        depth_complete = last_i

    # Save search info for last depth with complete mpv.
    cnt, fdata = 0, []
    for k, v in search_info.items():
        if f'd{depth_complete}_mpv' in k:
            cnt += 1
            fdata.append({cnt: v})
    return fdata


def create_epd_list(epd_fn):
    """ Read epd file and return a list in a format
        [fen, solutions, id, orig_epd_line]
    """
    fen_data = []
    num_good_epd_line = 0
    num_epd_line = 0
    
    with open(epd_fn, 'r') as f:
        for line in f:                
            epd_line = line.strip()
            epd = ' '.join(epd_line.split()[0:4])
            num_epd_line += 1
            
            logger.info('EPD position: {}'.format(num_epd_line))
            logger.info('EPD: {}'.format(epd_line))

            # Get solution line for epd with multiple good moves
            solutions = None
            try:
                # STS format
                # [pcs] w - - bm g5; id "epd id"; c0 "g5=10, Bd4=4, Kg8=4, Rd8=3";
                solutions = re.search('c0\s\"(.*?)\";', epd_line).group(1)
            except:
                logger.warning('Problem reading c0 field in epd: {}'.format(epd_line))
                logger.warning('This position is not included.')
                continue

            # Tony epd format
            # [pcs] w - - bm Kf2; c0 "positional scores are: Kf2=7, a4=3"; id "tony.pos.15";
            if ':' in solutions:
                solutions = solutions.split(':')[1]
            solutions = solutions.strip() # Nd2=10, h3=7, Be2=6
            
            if solutions is None:
                logger.warning('The following epd has no solution pts. epd: {}'.format(epd_line))
                logger.warning('This position is not included.')
                continue
            
            # Hack ignore the hmvc and fmvn
            fen = epd + ' 0 1'

            # Get id
            epd_id = None
            try:
                epd_id = re.search('id\s\"(.*?)\";', epd_line).group(1)
            except:
                pass

            logger.info('solutions: {}'.format(solutions))
            fen_data.append([fen, solutions, epd_id, epd_line])
            num_good_epd_line += 1

    return fen_data, num_good_epd_line, num_epd_line


def write_results_summary(out_fn, data, threadsval, hashval, movetime,
                          input_epd_path_and_file, input_epd_file, good_epd_cnt):
    """ Write results summary in text format """
    if not os.path.isfile(out_fn):
        with open(out_fn, 'a') as f:
            f.write('A. Engine settings\n')
            
            f.write('Threads        : %d\n' % threadsval)
            f.write('Hash (mb)      : %d\n' % hashval)
            f.write('Time(s)/pos    : %0.1f\n\n' % (float(movetime)/1000))


            f.write('B. Test set\n')
           
            f.write('Filename       : %s\n' % input_epd_file)
            f.write('NumPos         : %s\n\n' % good_epd_cnt)


            f.write('C. Results\n')
            
            f.write('%-32s : %6s  %5s  %7s  %8s  %5s  %8s  %9s\n' % (
                    'Engine', 'Rating', 'Top1', 'MaxTop1', 'Top1Rate',
                    'Score', 'MaxScore', 'ScoreRate'))

    logger.info('Writing analysis results ...')
    with open(out_fn, 'a') as f:
        for n in data:
            engine_name = n[0]
            top1_cnt = n[1]
            total_score = n[2]
            max_score = n[3]
            epd_cnt_tried = n[4]
            rating = n[6]

            top1_rate = 0.0
            if epd_cnt_tried:
                top1_rate = float(top1_cnt)/epd_cnt_tried
            
            score_rate = 0.0
            if max_score:
                score_rate = float(total_score)/max_score
            f.write('%-32s : %6d  %5d  %7d  %8.3f  %5d  %8d  %9.3f\n' % (
                    engine_name, rating, top1_cnt, epd_cnt_tried,
                    top1_rate, total_score, max_score, score_rate))
            

def write_results_in_csv(csv_fn, ana_data,
                         ana_time, engine_numhash,
                         engine_numthreads, temp_csv_fn):
    # Write to csv file
    if not os.path.isfile(csv_fn):
        with open(csv_fn, 'a') as f:
            f.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % ('Engine', 'Rating',
                    'Top1', 'MaxTop1', 'Top1Rate', 'Score', 'MaxScore',
                    'ScoreRate', 'MoveTime(ms)', 'Hash(MB)', 'Threads'))
            
    with open(csv_fn, 'a') as f:
        for n in ana_data:
            engine_name = n[0]
            top1_cnt = n[1]
            total_score = n[2]
            max_score = n[3]
            epd_cnt_tried = n[4]
            rating = n[6]

            top1_rate = 0.0
            if epd_cnt_tried:
                top1_rate = float(top1_cnt)/epd_cnt_tried
            
            score_rate = 0.0
            if max_score:
                score_rate = float(total_score)/max_score
            f.write('%s,%d,%d,%d,%0.3f,%d,%d,%0.3f,%d,%d,%d\n' % (engine_name,
                    rating, top1_cnt, epd_cnt_tried, top1_rate, total_score,
                    max_score, score_rate, ana_time, engine_numhash,
                    engine_numthreads))

    # Create html table from csv
    # Sort csv data by top1, score, movetime, hash, threads
    csv_data = []
    csv_data_header = []
    linecnt = 0
    with open(csv_fn, 'r') as f:
        for lines in f:
            linecnt += 1
            line = lines.strip()
            splitv = line.split(',')
                
            if linecnt == 1:
                csv_data_header.append(splitv)
            if linecnt >= 2:
                cnt = 0
                a = []
                for j in splitv:
                    cnt += 1
                    if cnt == 1:
                        val = j
                    elif cnt == 5 or cnt == 8:
                        val = float(j)
                    else:
                        val = int(j)
                    a.append(val)
                csv_data.append(a)

    csv_data = sorted(csv_data, key=sort_key_top1, reverse=True)
    csv_data = sorted(csv_data, key=sort_key_score, reverse=True)

    delete_file(temp_csv_fn)
    
    with open(temp_csv_fn, 'a') as f:
        for n in csv_data_header:
            f.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n'\
                    %('Rank', n[0], n[1], n[2], n[3], n[4], n[5], n[6],
                      n[7], n[8], n[9], n[10]))

    with open(temp_csv_fn, 'a') as f:
        cnt = 0
        for n in csv_data:
            cnt += 1
            engine_name = n[0]
            rating = int(n[1])
            top1 = int(n[2])
            maxtop1 = int(n[3])
            top1rate = float(n[4])
            score = int(n[5])
            maxscore = int(n[6])
            scorerate = float(n[7])
            movetime = int(n[8])
            hashval = int(n[9])
            threadsval = int(n[10])
            
            f.write('%d,%s,%d,%d,%d,%0.3f,%d,%d,%0.3f,%d,%d,%d\n' % (
                    cnt, engine_name, rating, top1, maxtop1, top1rate,
                    score, maxscore, scorerate, movetime, hashval, threadsval))
            
def main():
    parser = argparse.ArgumentParser(description=APP_DESC, epilog=APP_NAME_VERSION)
    parser.add_argument('-i', '--epd', help='input epd filename', required=True)
    parser.add_argument('-o', '--output', default='mea_results.txt',
                        help='text output filename for result, default=mea_results.txt')
    parser.add_argument('-e', '--engine', help='engine filename', required=True)
    parser.add_argument('--eoption', 
       help='uci engine option, --eoption "contempt=true, ' +
       'Futility Pruning=false, pawn value=120"', required=False)
    parser.add_argument('-n', '--name', help='engine name', required=True)
    parser.add_argument('-t', '--threads', default=1,
                        help='Threads or cores to be used by the engine, ' +
                        'default=1.', type=int)
    parser.add_argument('-m', '--hash', default=64,
            help='Hash in MB to be used by the engine, default=64.', type=int)
    parser.add_argument('-a', '--movetime', default=500,
        help='Analysis time in milliseconds, 1s = 1000ms, default=500', type=int)
    parser.add_argument('-r', '--rating', default=2500, 
        help='You may input a rating for this engine, this will be shown ' +
        'in the output file, default=2500', type=int)
    parser.add_argument('-p', '--protocol', default='uci',
                        help='engine protocol [uci/xboard], default=uci')
    parser.add_argument('-s', '--san', default=0,
        help='for xboard engine, set this to 1 if it will send a move ' +
        'in san format, default=0', type=int, choices=[0, 1])
    parser.add_argument('--stmode', default=1,
        help='for xboard engines, set this to 0 if it does not support ' +
        'st command, default=1', type=int, choices=[0, 1])
    parser.add_argument('--protover', default=2,
        help='for xboard engines, this is protocol version number, default=2',
        type=int, choices=[1, 2])
    parser.add_argument('--infinite', help='Run uci engine with go infinite',
                        action='store_true')
    parser.add_argument('--log', help='Records engine and analyzer output ' +
                        'to [engine name]_[movetime]_log.txt',
                        action='store_true')
    parser.add_argument('--runenginefromcwd', help='Run engine from mea folder',
                        action='store_true')
    parser.add_argument('--version', '-V', action='version', version=f"{__version__}")

    # Get values from arguments    
    args = parser.parse_args()
    input_epd_fn = args.epd  # Can have path like .\epd\test.epd
    output_summary_fn = args.output
    engine_fn = args.engine
    engine_numthreads = args.threads
    engine_numhash = args.hash
    ana_time = args.movetime
    engine_rating = args.rating
    proto = args.protocol
    eoption = args.eoption
    
    ana_data = []
    multipv = 1
    csv_fn = output_summary_fn[0:-4] + '.csv'
    html_fn = output_summary_fn[0:-4] + '.html'
    
    # If there is engine options in command line, find the hash and threads
    # value, we will use this as info in csv and html table
    if eoption:
        opt_list = eoption.split(',')
        for o in opt_list:
            opt = o.strip()
            name = opt.split('=')[0].strip()
            value = opt.split('=')[1].strip()            
            if name.lower() == 'hash':
                engine_numhash = int(value)
            elif name.lower() == 'threads':
                engine_numthreads = int(value)
            elif name.lower() == 'multipv':
                multipv = int(value)
    
    # Prepare filenames
    input_epd_file = os.path.basename(args.epd) # filename alone with extension
    input_epd_name = input_epd_file[0:-4]  # filename alone without extension
    
    # Only create log file if there is --log
    if args.log:
        # Declare log filename and replace forward, backward, and empty chars with underscore
        log_fn = '{}_multipv{}_{}_mt{}ms_log.txt'.format(input_epd_name, multipv,
                         args.name, ana_time)
        for r in ((' ', '_'), ('/', '_'), ('\\', '_')):
            log_fn = log_fn.replace(*r)
        
        fh = logging.FileHandler(log_fn, mode='w')
        formatter = logging.Formatter('[%(asctime)24s - %(levelname)8s ] %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    # Declare epd output filename (saving bm, ce and acd) and replace other chars in it
    if multipv > 1:
        epd_output_fn = '{}_multipv{}_{}_mt{}ms_epd.epd'.format(
                input_epd_name, multipv, args.name, ana_time)
    else:
        epd_output_fn = '{}_{}.epd'.format(input_epd_name, args.name)
    for r in ((' ', '_'), ('/', '_'), ('\\', '_')):
        epd_output_fn = epd_output_fn.replace(*r)
    delete_file(epd_output_fn)
    
    # Covert epd file to a list
    fen_list, good_epd_cnt, total_epd_cnt = create_epd_list(args.epd)
    if good_epd_cnt != total_epd_cnt:
        logger.warning('Total positions in the input epd are not being considered.')
        
    # Analyze the epd
    a = Analyze(engine_fn, fen_list, good_epd_cnt, ana_time, engine_numthreads,
                 engine_numhash, proto, args.name, args.san, args.stmode,
                 args.protover, epd_output_fn, multipv, eoption, input_epd_name,
                 args.infinite, args.runenginefromcwd)
    
    start_time = time.perf_counter()  # Python v3.3 and up
    a.run()
    end_time = time.perf_counter()
    
    elapsed = end_time - start_time             
    v = a.get_result()  # [engine, top1cnt, score, maxscore, numpostried]
    v.insert(len(v), elapsed)  # [engine, top1cnt, score, maxscore, numpostried, elapsed]
    v.insert(len(v), engine_rating) # [engine, top1cnt, score, maxscore, numpostried, elapsed, rating]
    ana_data.append(v)

    temp_csv_fn = 'temp_csv_results.csv'
    write_results_summary(output_summary_fn, ana_data, engine_numthreads,
                          engine_numhash, ana_time, args.epd, input_epd_file,
                          good_epd_cnt)
    write_results_in_csv(csv_fn, ana_data, ana_time, engine_numhash,
                         engine_numthreads, temp_csv_fn)

    delete_file(html_fn)        
    csv_to_html(temp_csv_fn, html_fn, input_epd_fn)
    delete_file(temp_csv_fn)
    logger.info('Done!!')
    logging.shutdown()
    
    move_file('epd_out', epd_output_fn)
    if args.log:
        move_file('log', log_fn) 


if __name__ == '__main__':
    main()
