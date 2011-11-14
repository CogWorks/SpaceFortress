from __future__ import division
import sys, os, math, numpy, itertools

ROI_NAMES = ["score_flight","score_fortress","score_vlner","score_intrvl","score_bonus","score_mine","score_iff","score_shots","bonus","ship","mine","fortress"]
FIX_CODE_NAMES = ["1","2","3","4","5","6","7","8","B","S","M","F"]
KEY_CODE_NAMES = ['l','r','t','f','i','s','p']

def get_runs(data):
    return [k for (k,g) in itertools.groupby(data)]

def remove_values_from_list(the_list, val):
    while val in the_list:
        the_list.remove(val)
    return the_list

def distance2point( x, y, viewerDistance, viewerHeight, resolutionX, resolutionY, screenWidth, screenHeight ):
    
    centerX = screenWidth / 2
    centerY = screenHeight / 2 - viewerHeight
    
    targetX = x / resolutionX * screenWidth
    targetY = y / resolutionY * screenHeight
    
    dX = targetX - centerX
    dY = targetY - centerY
    
    screenDistance = math.sqrt( dX**2 + dY**2 )
    
    return math.sqrt( ( viewerDistance**2 + screenDistance**2) )

def subtendedAngle(motion, x1, y1, x2, y2, viewerDistance=58.74, viewerHeight=4.55, resolutionX=1280, resolutionY=1024, screenWidth=33.97, screenHeight=27.31 ):
    
    if motion == 1:
    
        d1 = distance2point(x1, y1, viewerDistance, viewerHeight, resolutionX, resolutionY, screenWidth, screenHeight)
        d2 = distance2point(x2, y2, viewerDistance, viewerHeight, resolutionX, resolutionY, screenWidth, screenHeight)
        
        dX = screenWidth * ( ( x2 - x1 ) / resolutionX )
        dY = screenWidth * ( ( y2 - y1 ) / resolutionY )
        
        screenDistance = math.sqrt( dX**2 + dY**2 )
        
        angleRadians = math.acos( ( d1**2 + d2**2 - screenDistance**2 ) / ( 2 * d1 * d2 ) )
        
        return ( angleRadians / ( 2 * math.pi ) ) * 360

    else:
        
        return 99999

def getScoreLocations(header, data):
    
    scores = []

    for d in data:
        if d[header['e1']][:5] == 'score':
            scores.append((int(d[header['e2']]),int(d[header['e3']])))
        if len(scores)==8:
            return scores
        

def splitGames(header, data):
    i = 0
    nrow = len(data)
    games = []
    game = None
    current_game = 0
    while i < nrow:
        g = int(data[i][header['current_game']])
        if g != current_game:
            current_game = g
            if game:
                games.append(game)
            game = []
        if g > 0:
            game.append(data[i])
        i += 1
    return games

def splitMines(header, data):
    i = 0
    nrow = len(data)
    mines = []
    mine = None
    current_mine = 0
    while i < nrow:
        m = data[i][header['mine_no']]
        if m != 'NA':
            m = int(m)
            if m != current_mine:
                current_mine = m
                if mine:
                    mines.append(mine)
                mine = []
            if m > 0:
                mine.append(data[i])
        i += 1
    mines.append(mine)
    return mines

def splitBonuses(header, data):
    i = 0
    nrow = len(data)
    bonuses = []
    bonus = None
    current_bonus = 0
    while i < nrow:
        b = data[i][header['bonus_no']]
        if b != 'NA':
            b = int(b)
            if b != current_bonus:
                current_bonus = b
                if bonus:
                    bonuses.append(bonus)
                bonus = []
            if b > 0:
                bonus.append(data[i])
        i += 1
    bonuses.append(bonus)
    return bonuses

def eventORroi(header, scores, data, print_events=False):
    if data[0] == 'STATE':
        if len(header) == len(data):
            rois = []
            for score in scores:
                sa = subtendedAngle(int(data[header['eye_motion_state']]), float(data[header['fix_x']]), float(data[header['fix_y']]), score[0], score[1], viewerDistance=54)
                rois.append(sa)
            extras = [(data[header['bonus_cur_x']], data[header['bonus_cur_y']]),
                      (data[header['ship_x']], data[header['ship_x']]),
                      (data[header['mine_x']], data[header['mine_x']]),
                      (640,480)]
            for ex in extras:
                try:
                    rois.append(subtendedAngle(int(data[header['eye_motion_state']]), float(data[header['fix_x']]), float(data[header['fix_y']]), float(ex[0]), float(ex[1]), viewerDistance=54))
                except ValueError:
                    rois.append(99999)
            idx = numpy.array(rois).argmin()
            name = ROI_NAMES[idx]
            code = FIX_CODE_NAMES[idx]
            if name == 'mine':
                if data[header['mine_id']] in data[header['foes']].split(' '):
                    name = 'mine_foe'
                else:
                    name = 'mine_friend'
            elif name == 'bonus':
                name = "bonus_%s%s" % (data[header['bonus_prev']],data[header['bonus_cur']])
            return name,code,1
        else:
            return None,None,0
    elif print_events and data[header['e1']] == 'press':
        code = data[header['e2']][0]
        return '%s_%s' % (data[header['e1']],data[header['e2']]),code,2
    else:
        return None,None,0

def getMineSegmentSequences(header, data):
    print 'm_total\tgame\ttype\tm_game\tlen\tn_fix\tn_key\tstring\tsequence'
    scores = getScoreLocations(header, data)
    games = splitGames(header, data)
    mt = 0
    for g in range(0,len(games)):
        mines = splitMines(header, games[g])
        for m in range(0,len(mines)):
            if mines[m][0][header['mine_id']] in mines[m][0][header['foes']].split(' '):
                type = "foe"
            else:
                type = "friend"
            mt += 1
            rois = []
            codes = []
            for i in range(0,len(mines[m])):
                roi,code,t = eventORroi(header, scores, mines[m][i], print_events=False)
                rois.append(roi)
                codes.append(code)
            codes = ''.join(get_runs(remove_values_from_list(codes, None)))
            rois = ' '.join(get_runs(remove_values_from_list(rois, None)))
            nf = 0
            nk = 0
            for c in FIX_CODE_NAMES:
                nf += codes.count(c)
            for c in KEY_CODE_NAMES:
                nk += codes.count(c)
            print '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (mt, g+1, type, m+1, len(codes), nf, nk, codes, rois)
            
def getBonusSegmentSequences(header, data):
    
    scores = getScoreLocations(header, data)
    games = splitGames(header, data)
    bt = 0
    for g in range(0,len(games)):
        bonuses = splitBonuses(header, games[g])
        for b in range(0,len(bonuses)):
            if bonuses[b][0][header['bonus_prev']] == '#' and bonuses[b][0][header['bonus_cur']] == '$':
                type = "available"
            else:
                type = "unavailable"
            bt += 1
            rois = [eventORroi(header, scores, bonuses[b][i], print_events=False) for i in range(0,len(bonuses[b]))]
            print '%s\t%s\t%s\t%s\t%s' % (bt, g+1, type, b+1, ' '.join(get_runs(remove_values_from_list(rois, None))))

def process_log(filename):
    
    file = open(filename, 'r')
    base = os.path.splitext(filename)[0]
    data = []
    line = file.readline()
    prev_cells = None
    while line:
        cells = line[:-1].split('\t')
        if cells[0] == 'STATE':
            prev_cells = cells
        else:
            if prev_cells != None:
                cells = cells + prev_cells[8:]    
        line = file.readline()
        data.append(cells)                
    file.close()
    header = {}
    for i in range(0,len(data[0])):
        header[data[0][i]] = i
    getMineSegmentSequences(header, data[1:])
    #getBonusSegmentSequences(header, data[1:])
    
    #new.write('\t'.join(cells)+'\n')
    #new = open("%s.%s%s" % (tmp[0],'sequence',tmp[1]), 'w')
    #new.close()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        process_log(sys.argv[1])