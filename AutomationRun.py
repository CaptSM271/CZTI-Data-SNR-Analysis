import sys
import subprocess as sp

arguments=sys.argv

n = len(arguments)-1
if n<1:
    raise Exception('Inputs are missing.')

#RunBB.py abcd interval filename

intervals=[200, 50, 20, 10]

name=arguments[1]

binsizelist={'a':'0.01','b':'0.1','c':'1','d':'10'} #in seconds

print('Hi :->','I will be generating the light curves using Pipeline V3 modules for '+str(n)+' events, namely:',name,sep='\n')

#AS1A06_002T02_9000003206_21631czt

def Fcztgtigen(name,evt,mkf,mkfthresh):
    outfile=name+'_gtigen.evt'
    
    result=sp.run(['cztgtigen',
            'eventfile='+evt,
            'mkffile='+mkf,
            'thresholdfile='+mkfthresh,
            'outfile='+outfile,
            'usergtifile=-',
            'clobber=YES',
            'history=YES'])
    
    return result, outfile

def Fcztdatasel(name,evt,gtigen):
    outfile=name+'_bc_ds.evt'
        
    result=sp.run(['cztdatasel',
                   'infile='+evt,
                   'gtifile='+gtigen,
                   'gtitype=QUAD',
                   'outfile='+outfile,
                   'clobber=YES',
                   'history=YES'])
    
    return result, outfile

def Fcztpixclean(name, bcdsevt, bclivetime):
    quadpc=name+'_quad_pc.evt'
    quadlivetime=name+'_quad_livetime.fits'
    badpix=name+'_quad_badpix.fits'
    
    result=sp.run(['cztpixclean',
                   'infile='+bcdsevt,
                   'inlivetimefile='+bclivetime,
                   'writedblevt=YES',
                   'outfile1='+quadpc,
                   'outlivetimefile='+quadlivetime,
                   'badpixfile='+badpix,
                   'det_tbinsize=1',
                   'pix_tbinsize=1',
                   'det_count_thresh=100',
                   'pix_count_thresh=1000'])
    
    return result, quadpc, quadlivetime, badpix

def Fcztevtclean(name, quadpc):
    quadclean=name+'_quad_clean.evt'
    
    result=sp.run(['cztevtclean',
                   'infile='+quadpc,
                   'outfile='+quadclean,
                   'alphaval=0',
                   'vetorange=0-0',
                   'IsdoubleEvent=NO',
                   'clobber=YES',
                   'history=YES'])
    
    return result, quadclean

def Fcztflagbadpix(name, badpix):
    badpixflag=name+'_quad_badpix_flag.fits'
    
    result=sp.run(['cztflagbadpix',
                   'nbadpixFiles=1',
                   'badpixfile='+badpix,
                   'outfile='+badpixflag,
                   'clobber=YES',
                   'history=YES'])
    #debug
    return result, badpixflag

def Fcztbindata(name, quadlivetime, mkf, quadclean, badpixflag, binsize, emin, emax, interval, n):
    quadlightcurve=name+'_quad_lightcurve_'+binsize+'_'+str(interval)+'_'+str(n)
    quadmasks=name+'_quad_maskweights_'+binsize+'_'+str(interval)+'_'+str(n)
    emin=str(emin)
    emax=str(emax)
    
    result=sp.run(['cztbindata',
                   'inevtfile='+quadclean,
                   'mkffile='+mkf,
                   'badpixfile='+badpixflag,
                   'badpixThreshold=0',
                   'livetimefile='+quadlivetime,
                   'outputtype=lc',
                   'generate_eventfile=YES',
                   'timebinsize='+binsizelist[binsize],
                   'outfile='+quadlightcurve,
                   'outevtfile='+quadmasks,
                   'emin='+emin,
                   'emax='+emax,
                   'maskWeight=NO',
                   'rasrc=0',
                   'decsrc=0',
                   'deltatx=0',
                   'deltaty=0',
                   'clobber=YES',
                   'history=YES',
                   'debug=NO'])
    
    return result, quadlightcurve, quadmasks
            
print('','@'*90,sep='\n')
print('Starting to Process',name,'.')
print('@'*90,'',sep='\n')

mkf         = name+'_level2.mkf'
evt         = name+'M0_level2_bc.evt'
bclivetime  = name+'M0_level2_bc_livetime.fits'
mkfthresh   = 'mkfThresholds.txt'

result, gtigen = Fcztgtigen(name,evt,mkf,mkfthresh)

if result.returncode == 1:
    raise Exception('Error in cztgtigen')
else:
    print('','@'*90,'cztgtigen done!','@'*90,'',sep='\n')
    
result, bcdsevt = Fcztdatasel(name,evt,gtigen)

if result.returncode == 1:
    raise Exception('Error in cztdatasel')
else:
    print('','@'*90,'cztdatasel done!','@'*90,'',sep='\n')
    
result, quadpc, quadlivetime, badpix = Fcztpixclean(name, bcdsevt, bclivetime)

if result.returncode == 1:
    raise Exception('Error in cztpixclean')
else:
    print('','@'*90,'cztpixclean done!','@'*90,'',sep='\n')
    
result, quadclean = Fcztevtclean(name, quadpc)

if result.returncode == 1:
    raise Exception('Error in cztevtclean')
else:
    print('','@'*90,'cztevtclean done!','@'*90,'',sep='\n')
    
result, badpixflag = Fcztflagbadpix(name, badpix)

if result.returncode == 1:
    raise Exception('Error in cztflagbadpix')
else:
    print('','@'*90,'cztflagbadpix done!','@'*90,'',sep='\n')


for i in 'bc':

    for dE in intervals:
        n=1
        
        emin=20
        emax=20+dE
    
        while(True):
            result, quadlightcurve, quadmasks = Fcztbindata(name, quadlivetime, mkf, quadclean, badpixflag, i, emin, emax, dE, n)
    
            if result.returncode == 1:
                raise Exception('Error in cztbindata '+i+str(emin)+str(emax))
                
            print('','@'*90,'cztbindata done for',i,'and energy',dE,'list',n,'!','@'*90,'',sep='\n')
            print('\n\n')
            emin=emax
            emax=emax+dE
            n+=1
            if emax>220:
                break
    
            
        
    
        
    print('Processing',name,'has been done.')
    print('><'*90,'',sep='\n')
    
