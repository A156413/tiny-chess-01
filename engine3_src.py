import os,sys,json,random,time
from urllib.request import Request,urlopen
VAL={'P':100,'N':320,'B':330,'R':500,'Q':900,'K':0}
PST={'P':[0,0,0,0,50,50,50,50,10,10,20,30,5,5,10,25,0,0,0,20,5,-5,-10,0,5,10,10,-20,0,0,0,0],'N':[-50,-40,-30,-30,-40,-20,0,0,-30,0,10,15,-30,5,15,20,-30,0,15,20,-30,5,10,15,-40,-20,0,5,-50,-40,-30,-30],'B':[-20,-10,-10,-10,-10,0,0,0,-10,0,5,10,-10,5,5,10,-10,0,10,10,-10,10,10,10,-10,5,0,0,-20,-10,-10,-10],'R':[0,0,0,0,5,10,10,10,-5,0,0,0,-5,0,0,0,-5,0,0,0,-5,0,0,0,-5,0,0,0,0,0,0,5],'Q':[-20,-10,-10,-5,-10,0,0,0,-10,0,5,5,-5,0,5,5,0,0,5,5,-10,5,5,5,-10,0,5,0,-20,-10,-10,-5],'K':[-30,-40,-40,-50,-30,-40,-40,-50,-30,-40,-40,-50,-30,-40,-40,-50,-20,-30,-30,-40,-10,-20,-20,-20,20,20,0,0,20,30,10,0]}
PASSED=[0,60,35,20,12,6,3,0]
SCORE={}
for _ch,_tab in PST.items():
    for _sign,_pc in((1,_ch),(-1,_ch.lower())):
        _row=[0]*128
        for _s in range(128):
            if _s&0x88:continue
            _r,_f=_s>>4,_s&7
            _hf=_f if _f<4 else 7-_f
            _row[_s]=_sign*(VAL[_ch]+_tab[(_r if _sign>0 else 7-_r)*4+_hf])
        SCORE[_pc]=_row
_rng=random.Random(20261122)
ZK={p:[_rng.getrandbits(64)for _ in range(128)]for p in'PNBRQKpnbrqk'}
ZS=_rng.getrandbits(64)
ZC=[_rng.getrandbits(64)for _ in range(16)]
ZE=[_rng.getrandbits(64)for _ in range(8)]
CORNER={119:1,112:2,7:4,0:8}
ND=(-33,-31,-18,-14,14,18,31,33)
BD=(-17,-15,15,17)
RD=(-16,-1,1,16)
KD=BD+RD
def sqi(n):return(8-int(n[1]))*16+ord(n[0])-97
def sqn(s):return chr(97+(s&7))+str(8-(s>>4))
class Pos:
    __slots__=('b','t','c','e','hf','wk','bk','h','u')
    def __init__(self):self.b=['.']*128;self.u=[]
def fen(text):
    p=Pos();a=text.split();r=0
    for row in a[0].split('/'):
        c=0
        for ch in row:
            if ch.isdigit():c+=int(ch)
            else:
                p.b[r*16+c]=ch
                if ch=='K':p.wk=r*16+c
                if ch=='k':p.bk=r*16+c
                c+=1
        r+=1
    p.t=a[1];p.c=0
    for ch,bit in(('K',1),('Q',2),('k',4),('q',8)):
        if ch in a[2]:p.c|=bit
    p.e=sqi(a[3])if a[3]!='-'else-1
    p.hf=int(a[4])if len(a)>4 else 0
    h=0
    for s in range(128):
        if not s&0x88 and p.b[s]!='.':h^=ZK[p.b[s]][s]
    if p.t=='b':h^=ZS
    h^=ZC[p.c]
    if p.e>=0:h^=ZE[p.e&7]
    p.h=h
    return p
def atk(p,s,by_white):
    b=p.b
    for d in((15,17)if by_white else(-15,-17)):
        t=s+d
        if not t&0x88 and b[t]==('P'if by_white else'p'):return True
    for dirs,pc in((ND,'N'),(KD,'K')):
        for d in dirs:
            t=s+d
            if not t&0x88 and b[t]==(pc if by_white else pc.lower()):return True
    for dirs,kinds in((BD,'BQ'),(RD,'RQ')):
        for d in dirs:
            t=s+d
            while not t&0x88:
                c=b[t]
                if c!='.':
                    if c.isupper()==by_white and c.upper()in kinds:return True
                    break
                t+=d
    return False
def chk(p):return atk(p,p.wk if p.t=='w'else p.bk,p.t!='w')
def hit(p):return atk(p,p.wk if p.t=='b'else p.bk,p.t=='w')
DIRS={'N':(ND,0),'B':(BD,1),'R':(RD,1),'Q':(KD,1),'K':(KD,0)}
def gen(p,co=False):
    b=p.b;w=p.t=='w';ms=[]
    for s in range(128):
        if s&0x88:continue
        pc=b[s]
        if pc=='.'or pc.isupper()!=w:continue
        kind=pc.upper()
        if kind=='P':
            step=-16 if w else 16
            start_row,promo_row,row=(6,1,s>>4)if w else(1,6,s>>4)
            tg=[]
            if not co and b[s+step]=='.':
                tg.append(s+step)
                if row==start_row and b[s+2*step]=='.':ms.append((s,s+2*step,''))
            for d in(step-1,step+1):
                t=s+d
                if not t&0x88 and((b[t]!='.'and b[t].isupper()!=w)or t==p.e):tg.append(t)
            for t in tg:
                if row==promo_row:
                    for pr in'QRBN':ms.append((s,t,pr if w else pr.lower()))
                else:ms.append((s,t,''))
            continue
        dirs,slide=DIRS[kind]
        for d in dirs:
            t=s+d
            while not t&0x88:
                if b[t]=='.':
                    if not co:ms.append((s,t,''))
                else:
                    if b[t].isupper()!=w:ms.append((s,t,''))
                    break
                if not slide:break
                t+=d
        if kind=='K'and not co:
            home=116 if w else 4
            if s==home:
                rook='R'if w else'r';foe=not w
                sides=((1 if w else 4,home+3,(1,2),1),(2 if w else 8,home-4,(1,2,3),-1))
                for bit,rook_sq,gaps,sgn in sides:
                    if p.c&bit and b[rook_sq]==rook and all(b[home+g*sgn]=='.'for g in gaps)and not atk(p,home,foe)and not atk(p,home+sgn,foe):
                        ms.append((s,home+2*sgn,''))
    return ms
def make(p,m):
    frm,to,promo=m;b=p.b;pc=b[frm];cap=b[to];ep_sq=-1
    if pc.upper()=='P'and to==p.e and cap=='.'and(frm&7)!=(to&7):
        ep_sq=to+16 if pc.isupper()else to-16
        cap=b[ep_sq]
    p.u.append((m,cap,p.c,p.e,p.hf,ep_sq,p.h))
    h=p.h^ZS^ZC[p.c]
    if p.e>=0:h^=ZE[p.e&7]
    h^=ZK[pc][frm]
    if ep_sq>=0:h^=ZK[cap][ep_sq];b[ep_sq]='.'
    elif cap!='.':h^=ZK[cap][to]
    placed=promo if promo else pc
    h^=ZK[placed][to];b[to]=placed;b[frm]='.'
    if pc=='K':p.wk=to
    if pc=='k':p.bk=to
    if pc.upper()=='K'and abs(to-frm)==2:
        rf,rt=(frm+3,frm+1)if to>frm else(frm-4,frm-1)
        rook=b[rf];h^=ZK[rook][rf]^ZK[rook][rt];b[rt]=rook;b[rf]='.'
    cc=p.c
    if pc=='K':cc&=~3
    if pc=='k':cc&=~12
    cc&=~CORNER.get(frm,0);cc&=~CORNER.get(to,0)
    p.c=cc;h^=ZC[cc];p.e=-1
    if pc.upper()=='P'and abs(to-frm)==32:p.e=(frm+to)//2;h^=ZE[p.e&7]
    p.hf=0 if pc.upper()=='P'or cap!='.'else p.hf+1
    p.h=h;p.t='b'if p.t=='w'else'w'
def unmake(p):
    m,cap,cc,ep,hf,ep_sq,h=p.u.pop()
    frm,to,promo=m;b=p.b
    p.t='b'if p.t=='w'else'w'
    pc=b[to]
    if promo:pc='P'if p.t=='w'else'p'
    b[frm]=pc
    if ep_sq>=0:b[to]='.';b[ep_sq]=cap
    else:b[to]=cap
    if pc=='K':p.wk=frm
    if pc=='k':p.bk=frm
    if pc.upper()=='K'and abs(to-frm)==2:
        rf,rt=(frm+3,frm+1)if to>frm else(frm-4,frm-1)
        b[rf]=b[rt];b[rt]='.'
    p.c,p.e,p.hf,p.h=cc,ep,hf,h
def ev(p):
    b=p.b;score=0
    wpr=[0]*8;bpr=[0]*8
    pawns=[]
    for s in range(128):
        if s&0x88:continue
        pc=b[s]
        if pc=='.':continue
        score+=SCORE[pc][s]
        kind=pc.upper()
        if kind=='P':
            pawns.append((s,pc.isupper()))
            if pc.isupper():wpr[s&7]|=1<<(s>>4)
            else:bpr[s&7]|=1<<(s>>4)
    for s,is_w in pawns:
        f,r=s&7,s>>4
        if is_w:foe_r,sign=bpr,1;ahead=(1<<r)-1
        else:foe_r,sign=wpr,-1;ahead=~((1<<(r+1))-1)
        xtra=0
        near=foe_r[f]|(foe_r[f-1]if f>0 else 0)|(foe_r[f+1]if f<7 else 0)
        if not near&ahead&0xFF:xtra+=PASSED[r]if sign>0 else PASSED[7-r]
        score+=sign*xtra
    return score if p.t=='w'else-score
MATE=100000
NB=300000
QB=420000
nodes=[0]
tt={}
killers=[[None,None]for _ in range(128)]
END=[0.0]
class OutOfNodes(Exception):pass
def order(p,ms,tm,ply):
    b=p.b;scd=[]
    for m in ms:
        if m==tm:sc=9000000
        elif b[m[1]]!='.'or m[1]==p.e:
            victim=b[m[1]]if b[m[1]]!='.'else'P'
            sc=1000000+VAL[victim.upper()]*10-VAL[b[m[0]].upper()]//10
            if m[2]:sc+=VAL[m[2].upper()]
        elif ply<128 and m==killers[ply][0]:sc=900000
        elif ply<128 and m==killers[ply][1]:sc=800000
        else:sc=0
        scd.append((sc,m))
    scd.sort(key=lambda x:-x[0])
    return[m for _,m in scd]
def qs(p,alpha,beta,ply):
    nodes[0]+=1
    if nodes[0]>QB or(nodes[0]&1023)==0 and time.time()>END[0]:raise OutOfNodes
    checked=chk(p)
    if not checked:
        sp=ev(p)
        if sp>=beta:return beta
        if sp>alpha:alpha=sp
    legal=0
    for m in order(p,gen(p,not checked),None,ply):
        tgt=p.b[m[1]]
        if not checked and tgt!='.'and m[1]!=p.e and not m[2]and sp+VAL[tgt.upper()]+200<alpha:continue
        make(p,m)
        if hit(p):unmake(p);continue
        legal+=1
        sc=-qs(p,-beta,-alpha,ply+1)
        unmake(p)
        if sc>=beta:return beta
        if sc>alpha:alpha=sc
    if checked and not legal:return-MATE+ply
    return alpha
def search(p,depth,alpha,beta,ply,can_null=True):
    if p.hf>=100:return 0
    if depth<=0:return qs(p,alpha,beta,ply)
    nodes[0]+=1
    if ply>0 and(nodes[0]>NB or(nodes[0]&1023)==0 and time.time()>END[0]):
        raise OutOfNodes
    entry=tt.get(p.h);tm=None
    if entry:
        tm=entry[3]
        if entry[0]>=depth and ply>0:
            if entry[1]==0:return entry[2]
            if entry[1]==1:alpha=max(alpha,entry[2])
            if entry[1]==2:beta=min(beta,entry[2])
            if alpha>=beta:return entry[2]
    checked=chk(p)
    if checked:depth+=1
    if can_null and not checked and depth>=3 and ply>0 and any(c in'NBRQnbrq'for c in p.b):
        if ev(p)>=beta:
            saved_e,saved_h=p.e,p.h
            if p.e>=0:p.h^=ZE[p.e&7]
            p.e=-1;p.h^=ZS;p.t='b'if p.t=='w'else'w'
            sc=-search(p,depth-3,-beta,-beta+1,ply+1,False)
            p.t='b'if p.t=='w'else'w';p.e,p.h=saved_e,saved_h
            if sc>=beta:return beta
    bs=-10**9;bm=None;flag=2;legal=0
    for idx,m in enumerate(order(p,gen(p),tm,ply)):
        is_cap=p.b[m[1]]!='.'or m[1]==p.e
        make(p,m)
        if hit(p):unmake(p);continue
        legal+=1
        if legal==1:
            sc=-search(p,depth-1,-beta,-alpha,ply+1)
        elif depth>=3 and idx>3 and not is_cap and not checked:
            sc=-search(p,depth-2,-alpha-1,-alpha,ply+1)
            if sc>alpha:
                sc=-search(p,depth-1,-alpha-1,-alpha,ply+1)
                if alpha<sc<beta:sc=-search(p,depth-1,-beta,-alpha,ply+1)
        else:
            sc=-search(p,depth-1,-alpha-1,-alpha,ply+1)
            if alpha<sc<beta:sc=-search(p,depth-1,-beta,-alpha,ply+1)
        unmake(p)
        if sc>bs:bs=sc;bm=m
        if sc>alpha:
            alpha=sc;flag=0
            if alpha>=beta:
                flag=1
                if not is_cap and ply<128 and killers[ply][0]!=m:
                    killers[ply][1]=killers[ply][0];killers[ply][0]=m
                break
    if not legal:return-MATE+ply if checked else 0
    tt[p.h]=(depth,flag,bs,bm)
    return bs
def best(sf,played):
    p=fen(sf)
    for text in played:
        promo=''
        if len(text)>4:promo=text[4].upper()if p.t=='w'else text[4]
        make(p,(sqi(text[:2]),sqi(text[2:4]),promo))
    tt.clear()
    for k in killers:k[0]=k[1]=None
    nodes[0]=0
    END[0]=time.time()+3.6
    bm=None;depth=1
    while depth<=40:
        entry=tt.get(p.h)
        tm=entry[3]if entry else None
        alpha=-10**9;cm=None;cs=-10**9
        try:
            for m in order(p,gen(p),tm,0):
                make(p,m)
                if hit(p):unmake(p);continue
                sc=-search(p,depth-1,-10**9,-alpha,1)
                unmake(p)
                if sc>cs:cs=sc;cm=m
                if sc>alpha:alpha=sc
        except OutOfNodes:break
        if cm:bm=cm;tt[p.h]=(depth,0,cs,cm)
        if nodes[0]>NB:break
        depth+=1
    return bm
def uci(m):return sqn(m[0])+sqn(m[1])+(m[2].lower()if m[2]else'')
def main():
    env=os.environ.get('MAKEFUN_ENV_URL')or sys.exit('no env')
    def post(path,body):
        req=Request(env+path,data=json.dumps(body).encode(),headers={'content-type':'application/json'})
        with urlopen(req,timeout=30)as resp:return json.loads(resp.read())
    while True:
        g=post('/game',{})
        if g.get('status')=='done':break
        while g.get('status')=='your_move':
            m=best(g['start_fen'],g['moves'])
            if m is None:post('/resign',{'game':g['game']});break
            g=post('/move',{'game':g['game'],'move':uci(m)})
            if g.get('status')=='over':break
        if g.get('status')=='done':break
if __name__=='__main__':main()
