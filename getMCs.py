#!/usr/bin/python

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("campaign", help="The MC Campaign")
args = parser.parse_args()

def checkExist(gs,i):
    return len(gs['reqmgr_name'])>0 and  ('content' in   gs['reqmgr_name'][i]) and ('pdmv_status_history_from_reqmngr' in gs['reqmgr_name'][i]['content'])


#Get all the steps from the chain name
def getSteps(allRequests, ch):
    reqs = []
    for r in allRequests:
        if ch in r['member_of_chain']:
            reqs.append(r)

    if len(reqs) > 5:
        print "Length is ", len(reqs)
        for a in reqs:
            print r['prepid']
        assert(0)
    fs = lhe = gs = dr = reReco = mini = nano = None
    for r in reqs:
        if 'wmLHE-' in r['prepid']:
            lhe = r
        elif 'GS-' in r['prepid']:
            gs = r
        elif 'DR' in r['prepid']:
            dr = r
        elif 'ReReco' in r['prepid']:
            reReco = r
        elif 'MiniAOD' in r['prepid']:
            mini = r
        elif 'NanoAOD' in r['prepid']:
            nano = r
        elif 'FS' in r['prepid']:
            fs = r
            
    assert(((fs!=None) +  (lhe!=None) + (gs != None) + (dr!=None) + (reReco!=None) + (mini!=None) + (nano!=None)) == len(reqs))

    steps = []
    if lhe != None:
        steps.append((lhe, 'LHE'))
    if gs != None:
        steps.append((gs, 'GS'))
    if dr != None:
        steps.append((dr, 'DR'))
    if fs != None:
        steps.append((fs, 'FS'))
    if reReco != None:
        steps.append((reReco, 'ReReco'))
    if mini != None:
        steps.append((mini, 'MiniAOD'))
    if nano != None:
        steps.append((nano, 'NanoAOD'))

    middle = None
    if fs != None:
        middle = fs
    else:
        middle = dr

    assert(steps[0] != None)
    assert(middle   != None)
    assert(steps[-1]!= None)

    return (steps[0][0], middle,  steps[-1][0])




def getChains(allRequests):
    chains = {}
    for r in allRequests:
        dn = r['dataset_name']
        if dn not in chains:
            chains[dn] = set()
        for ch in  r['member_of_chain']:
            #print ch

            if 'GS' not in r['prepid'] and (r['status'] == 'submitted' or r['status'] == 'done'):
                chains[dn].add(ch)
    return chains

def getTagBare(r):
    pileUpStr = ''
    for  x in r['sequences']:
        if 'pileup' in x:
            pileUpStr +=  x['pileup']
    pileUpFile =  r['pileup_dataset_name'][0:r['pileup_dataset_name'].rfind("/")]

    tagMain = ''
    for x in  r['output_dataset']:
        iS = x.find("/", 2)
        iE = x.rfind("/")
        x = x[iS+1:iE]
        iS = x.find("-")
        iE = x.rfind("-")
        tagMain += x[iS+1:iE]
    tagBr = ''
    if len(pileUpStr) > 2:
        tagBr += '&nbsp;('+pileUpStr[0:10]+')'
    tagMain = tagMain[0:30-len(tagBr)]
    return (tagMain+tagBr).strip()


def getTag(r,ch):
    #pileUp str in sequences
    pileUpStr = ''
    for  x in r['sequences']:
        if 'pileup' in x:
            pileUpStr +=  x['pileup']
    #pileUp file name
    pileUpFile =  r['pileup_dataset_name'][0:r['pileup_dataset_name'].rfind("/")]

    recTag='DR'
    if 'FSPremix' in ch:
        recTag = 'FS'
    #From output-file name
    tagFile = ''
    for x in  r['output_dataset']:
        iS = x.find("/", 2)
        iE = x.rfind("/")
        x = x[iS+1:iE]
        iS = x.find(recTag)
        iE = x.rfind("-")
        tagFile += x[iS+2:]

    if tagFile[:len(tagFile)/2] == tagFile[len(tagFile)/2:]:
        tagFile = tagFile[:len(tagFile)/2]
    import re
    tagFile = re.sub(r'^-', "", tagFile)

    tagBr = ''
    if len(pileUpStr) > 2:
        tagBr += '&nbsp;('+pileUpStr[0:10]+')'
    tagTrim = tagFile[0:30-len(tagBr)]
    tag = (tagTrim+tagBr).strip()
    if len(tag) < 4:
        tag = r['prepid']

    pileUpFile = pileUpFile.replace('-', '&#8209;') #there can be issues with -
    #if len(pileUpFile) > 2:

    tagCol = '#000000'
    if 'FlatPU' in tagFile:
        tagCol = '#ff9933'
    elif 'NoPU' in tagFile:
        tagCol = '#0000FF'
    elif 'realistic' in tagFile:
        tagCol = '#000000'

    import re
    #BTV-chain_RunIIFall18GS_flowRunIIFall18DRPremix_flowRunIIFall18MiniAOD_flowRunIIFall18NanoAOD-00013
    #HIG-chain_RunIIFall18wmLHEGS_flowRunIIFall18DRFlatPU0to70_flowRunIIFall18HEMreReco-00001

    chainTag = ''
    if 'reReco' in ch[:-6]:
        searchObj = re.search( r'_flowRunII[a-zA-Z]*1[5-9]'+recTag+'.*reReco', ch[:-6], re.M)
        if searchObj:
            chainTag = searchObj.group(0)
            searchObj = re.search( r''+recTag+'.*', chainTag, re.M)
            if searchObj:
                chainTag = searchObj.group(0)
                chainTag = re.sub(r'_flowRunII[A-Z][a-z]*1[5-9]', "&rarr;", chainTag)
                #print chainTag
                #import sys
                #sys.exit()
    else:
        searchObj = re.search( r'_flowRunII[a-zA-Z]*1[5-9]'+recTag+'[^_]*', ch[:-6], re.M)
        if searchObj:
            chainTag = searchObj.group(0)
            searchObj = re.search( r''+recTag+'[^_]*', chainTag, re.M)
            if searchObj:
                chainTag = searchObj.group(0)
        #print searchObj.group(1)
        #print searchObj.group(2)
    chainTag = re.sub(r'^'+recTag, "", chainTag)
    chainTag = re.sub(r'reReco$', "", chainTag)
    if chainTag == '':
        chainTag = '-'
    #print s
    #import sys
    #sys.exit()

    if pileUpStr != '':
        pileUpStr =' ('+pileUpStr+')'
    tag = '<span style="color:'+tagCol+'" title="'+tagFile+pileUpStr+'">'+chainTag+'</span>'
    return tag




def getEvnt(r):
    nEv = r['total_events']
    if nEv < 0.095e6:
        return str(int(round(nEv/1e3)))+'t'
    elif nEv < 0.95e6:
        return str(round(nEv/1e5)/10.)+'M'
    else:
        return str(int(round(nEv/1e6)))+'M'
    return ''


def getStatus(r):
    if r == None:
        return 0
    return round(abs((r['completed_events']+0.)/r['total_events']*100.),1)


def getStatusTab(r, nMerge = 1):
    if r == None:
        return "<td align=\"center\">-</td>"
    st = getStatus(r)
    if st == None:
        return "<td align=\"center\">-</td>"
    s = str(st)
    #sRef = '<a href="https://cms-pdmv.cern.ch/mcm/requests?prepid=' + r['prepid']+'">' + s +'</a>'
    sRef = '<a style="text-decoration: none" href="https://cms-pdmv.cern.ch/pmp/historical?r='+ r['prepid']+'">' + s +'</a>'
    if 'done' in r['status']:
        return "<td rowspan=\""+str(nMerge)+"\"  width=\"50px\" align=\"center\" class='withBGdone' style='background-size: "+s+"% 100%'>"+sRef+'</td>'
    else:
        return "<td rowspan=\""+str(nMerge)+"\" width=\"50px\" align=\"center\" class='withBG' style='background-size: "+s+"% 100%'>"+sRef+'</td>'









def getCampaign(name):
    import sys
    sys.path.append('/afs/cern.ch/cms/PPD/PdmV/tools/McM/')
    
    from rest import McM
    
    #mcm = restful(dev=False, cookie='dev-cookie.txt')
    mcm = McM(dev=False, cookie='cookies/cookie.txt')
    
    # example to search  ALL requesst which are member of a campaign
    # it uses a generic search for specified columns: query='status=submitted'
    # queries can be combined: query='status=submitted&member_of_campaign=Summer12'

    lines = []
    with open("lists/"+name+".txt") as f:
        lines = [line.rstrip('\n') for line in f]

    dataSets = []
    for d in lines:
        ds = d.strip()
        if len(ds) < 1: continue
        if ds[0] == "%": continue
        if ds[0] == "#":
            dataSets.append((ds[1:],[]))
        else:
            dataSets[-1][1].append(ds)

    #print "RADEK"
    #print dataSets
    #import sys
    #sys.exit()
    
    #lines = set(lines) #To have it unique

    allRequests = []
    for item in dataSets:
        for r in  item[1]:
            req = mcm.get('requests',query='dataset_name='+r+'&prepid=*-RunII'+name+'*')
            if req != None:
                allRequests += req

    chains = getChains(allRequests)

    for dn in chains:
        chAll = chains[dn]
        for ch in chAll:
            req = mcm.get('requests',query='member_of_chain='+ch)
            for r in req:
                #print ch, r['prepid']
                n = r['prepid']
                if 'GS-' in n:
                    pass
                elif 'DR' in n:
                    pass
                elif 'ReReco' in n:
                    pass
                elif 'MiniAOD' in n:
                    pass
                elif 'NanoAOD' in n:
                    pass
                else:
                    #print len(req), ch
                    print n

                if r not in allRequests:
                    allRequests.append(r)
                    #print 'Adding ',r['dataset_name'], r['prepid']
                else:
                    pass
                    #print 'Existing ',r['dataset_name'], r['prepid']

    #test
#    for r in allRequests:
#        if len(r['reqmgr_name']) > 1:
#            print r['reqmgr_name']
#            import sys
#            sys.exit()



    #allRequests =  allRequests1 +  allRequests2 + allRequests3 + allRequests4
    return (allRequests, dataSets)



allRequests, dataSets =  getCampaign(args.campaign)

#print allRequests[0]


def stringSplitByNumbers(rr):
    import re
    r = re.compile('(\d+)')
    l = r.split(rr['dataset_name'])
    return ([int(y) if y.isdigit() else y for y in l], rr['member_of_campaign'])

#Duplicity check
for a in allRequests:
    c = 0
    for b in allRequests:
        if a['prepid'] == b['prepid']:
            c += 1
    if c != 1:
        print a['prepid'], a['dataset_name']
        assert(0)


allRequests = sorted(allRequests, key=stringSplitByNumbers) 
chains = getChains(allRequests)

#print "RADEK"
#print chains



print '<html>'
print '<style> table, th, td { border: 1px solid black; }</style>'
print '<style> a { text-decoration: none; }</style>'
print '<style> .withBG     { background-image: linear-gradient(#FB00FF, #FB00FF, #FB00FF); background-repeat: no-repeat;}</style>'
print '<style> .withBGdone { background-image: linear-gradient(#87FF00, #87FF00, #87FF00); background-repeat: no-repeat;}</style>'
print '<style> .withBGval { background-image: linear-gradient(#C18080, #C18080, #C18080); background-repeat: no-repeat;}</style>'

menu = ''
for m in ['Summer17','Fall17','Summer18','Fall18']:
    menu += '<a href="'+m+'.html">'+m+'</a>, '

if args.campaign == "Summer18":
    print '<h1>Summer18 Campaign (CMSSW_10_1)</h1>'
    print '<p>'+menu+'check also related googledoc <a href="https://docs.google.com/spreadsheets/d/1NIWgppaC4WdxES3LZLvl8KBG1candg3BcIsA_cXvICc/edit#gid=5413440">status</a>, '
elif args.campaign == "Fall18":
    print '<h1>Fall18 Campaign (CMSSW_10_2)</h1>'
    print '<p>'+menu+'check also related googledoc <a href="https://docs.google.com/spreadsheets/d/1NIWgppaC4WdxES3LZLvl8KBG1candg3BcIsA_cXvICc/edit#gid=1551401330">status</a>, '
    print '<a href="https://docs.google.com/spreadsheets/d/1NIWgppaC4WdxES3LZLvl8KBG1candg3BcIsA_cXvICc/edit#gid=1681929127">planning</a> '
elif args.campaign == "Fall17":
    print '<h1>Fall17 Campaign (CMSSW_9_4)</h1>'
    print '<p>'+menu
elif args.campaign == "Summer17":
    print '<h1>Summer17 Campaign (CMSSW_9_3)</h1>'
    print '<p>'+menu


import datetime
from time import localtime, strftime
timeNow = strftime("%Y-%m-%d %H:%M:%S", localtime())
print'(last update: ',timeNow 
print ' )</p>'


print '<table>'
print '<tr>'
print '<td>type</td>'
print '<td>dataset name</td>'
print '<td>chainTag</td>'
print '<td>nEv</td>'
print '<td>Prior.</td>'
print '<td>S</td>'
print '<td>Run/Idle</td>'
print '<td>GS</td>'
print '<td>DR</td>'
print '<td>mAOD</td>'
print '<td>nAOD</td>'
print '<td>reReco</td>'
print '</tr>'

import collections
chains = collections.OrderedDict(sorted(chains.items()))
for item in dataSets:
    
    nChains = 0
    for dn in item[1]:
        if dn in chains:
            nChains += max(1,len(chains[dn]))
        else:
            nChains += 1
    #if item[0] == 'TT':
        #print nChains

    for dnId, dn in enumerate(item[1]):
        #print dn
        chAll = chains[dn] if dn in chains else []
        #sort by tag name
        chSort = []
        for ch in chAll:
            chSort.append(ch)

        def sortFun(ch):
            steps = getSteps(allRequests, ch)
            #gs =  steps[0]
            #print gs

            genName  = ''
            taskName = ''
            tag      = ''
            drPrepID = ''
            genName  = steps[0]['prepid']
            try:
                taskName = steps[-1]['reqmgr_name'][-1]['content']['pdmv_prep_id']
            except:
                pass
            tag      =  getTagBare(steps[1])
            drPrepID =  steps[1]['prepid']
            return (genName, taskName, drPrepID, tag)
            #taskName = ''
            #tag      = ''
            #drPrepID = ''
            #for r in allRequests:
            #    if ch in r['member_of_chain']:
            #        if 'GS' in r['prepid']:
            #            taskName = r['reqmgr_name'][-1]['content']['pdmv_prep_id']
            #        if 'DR' in r['prepid']:
            #            tag = getTagBare(r)
            #            drPrepID = r['prepid']
            #return (taskName, tag, drPrepID)
        chSort = sorted(chSort, key=sortFun) 

        if len(chAll) == 0:
            r = None
            for rN in allRequests:
                if dn == rN['dataset_name']:
                    r= rN
            print '<tr>'
            if dnId == 0:
                print '<td  rowspan="'+str(nChains)+ ' width=\"100px\"  ">',item[0],'</td>'
            if r != None:
                print '<td><a href="https://cms-pdmv.cern.ch/mcm/requests?prepid=' + r['prepid']+'">', dn, '</a></td>'
                print '<td></td>'
                print '<td>',getEvnt(r),'</td>'

                status = r['status']
                if r['approval'] == "validation":
                    if r['status'] == "new":
                        status = "validation"
                    elif r['status'] == "validation":
                        status = "validated"
                print '<td colspan=7>',status,'</td>'
            else:
                print '<td>', dn, '</td>'
                print '<td></td>'
                print '<td></td>'
                print '<td colspan=7 style="color:red">Not in system!</td>'


            print '</tr>'

        #Evaluate drMult
        drMult = ['']*len(chSort)
        for chId, ch in enumerate(chSort):
            for r in allRequests:
                if (ch in r['member_of_chain']) and ('DR' in r['prepid']):
                    drMult[chId] = r['prepid']
        assert(len(drMult) == len(chSort))
        for i in range(len(drMult)):
            val = drMult[i]
            if val == 0: continue
            c = 0
            while  i+c < len(drMult)  and  drMult[i+c] == val:
                drMult[i+c] = 0
                c+=1
            drMult[i] = c


        #Evaluate gsMult
        gsMult = {}
        for chId, ch in enumerate(chSort):
            for r in allRequests:
                if (ch in r['member_of_chain']) and ('GS' in r['prepid']):
                    if r['prepid'] not in gsMult:
                        gsMult[r['prepid']] = 0
                    gsMult[r['prepid']] += 1


        for chId, ch in enumerate(chSort):
            #print 'RADEK', dn, ch
            reqs = []
            for r in allRequests:
                if ch in r['member_of_chain']:
                    reqs.append(r)


            if len(reqs) > 5:
                print "Length is ", len(reqs)
                for a in reqs:
                    print r['prepid']
                assert(0)
            fs = lhe = gs = dr = reReco = mini = nano = None
            for r in reqs:
                if 'wmLHE-' in r['prepid']:
                    lhe = r
                elif 'GS-' in r['prepid']:
                    gs = r
                elif 'DR' in r['prepid']:
                    dr = r
                elif 'ReReco' in r['prepid']:
                    reReco = r
                elif 'MiniAOD' in r['prepid']:
                    mini = r
                elif 'NanoAOD' in r['prepid']:
                    nano = r
                elif 'FS' in r['prepid']:
                    fs = r
                    
            assert(((fs!=None) +  (lhe!=None) + (gs != None) + (dr!=None) + (reReco!=None) + (mini!=None) + (nano!=None)) == len(reqs))
            if fs != None:
                dr = gs = fs
            ref = dr if reReco == None else reReco

            if gs == None:
                print ch
                assert(0)
            assert(gs != None) 

            print '<tr>'
            if dnId == 0 and chId == 0:
                print '<td  rowspan="'+str(nChains)+ '" width=\"100px\" >',item[0],'</td>'
                #import sys
                #sys.exit()
            #print '<td>',item[0],'</td>'
            if chId == 0:
                #print '<td rowspan="'+str(len(chAll))+'">', dn, '</td>'
                print '<td rowspan="'+str(len(chAll))+'"><a href="https://cms-pdmv.cern.ch/mcm/requests?dataset_name=' + gs['dataset_name']+'&prepid=*'+ args.campaign +'*GS*">', dn, '</a></td>'
            #print '<td>',dn,'</td>'

            
            tagStr='<a href="https://cms-pdmv.cern.ch/mcm/requests?member_of_chain='+ch+'">'+getTag(dr,ch)+'</a>'
            print '<td>',tagStr,'</td>'
            print '<td>',getEvnt(r),'</td>'


            mytroArr = []
            for tmpId, tmp in enumerate(chSort):
                reqsTmp = []

                steps = getSteps(allRequests, tmp)
                try:
                    mytroArr.append(steps[-1]['reqmgr_name'][-1]['content']['pdmv_prep_id'])
                except:
                    mytroArr.append('notAvail'+str(tmpId))
                #for r in allRequests:
                #    if (tmp in r['member_of_chain']) and ('GS' in r['prepid']):
                #        mytroArr.append(r['reqmgr_name'][-1]['content']['pdmv_prep_id'])
            assert(len(chSort) == len(mytroArr))
            #print 'RADEK', mytroArr 
            prLen = -1
            if mytroArr[:chId].count(mytroArr[chId]) == 0:
                prLen = mytroArr[chId:].count(mytroArr[chId])



            #prCur = ref['reqmgr_name'][-1]['content']['pdmv_present_priority']
            prOld = ref['priority']
            #print 'RADEK', prCur, prOld
            priority=str(prOld/1000)+'K'
            runStat = ''
            if checkExist(ref,-1)  and ('force-complete' in ref['reqmgr_name'][-1]['content']['pdmv_status_history_from_reqmngr']):
                priority = 'FC'
            elif ref['status']=='done':
                priority = "done"
            if  (len(gs['reqmgr_name'])>0) and ('GS' in gs['prepid']):
                mytroId = gs['reqmgr_name'][-1]['content']['pdmv_prep_id']
                addr = 'https://dmytro.web.cern.ch/dmytro/cmsprodmon/workflows.php?prep_id='+mytroArr[chId]
                if priority == 'FC':
                    priority='<a href="'+addr+'" title="Force completition" style="color:red">'+priority+'</a>'
                else:
                    priority='<a href="'+addr+'">'+priority+'</a>'
                if 'notAvail' in mytroArr[chId]:
                    priority = '-'

                import os, sys
                myOut = os.popen("curl -s -L  "+addr).readlines()
                if len(myOut) > 10:
                    findStr = '<tr><td class=lpc>Production status</td><td class=lpc>'
                    runStat =  [l for l in myOut if findStr in l]
                    if len(runStat) > 0:
                        runStat = runStat[0][len(findStr):-11]
                    #print runStat
                    #sys.exit()

            if prLen > 0:
                RunIdle = []
                for i,kn in enumerate(ref['reqmgr_name']):
                    if checkExist(ref,i) and  ('completed' not in kn['content']['pdmv_status_history_from_reqmngr']):
                        #from subprocess import check_output
                        #myOut  = check_output(["curl", "-L", "--cookie", "cookie.txt", "--cookie-jar",  "cookie.txt", "https://cms-gwmsmon.cern.ch/prodview/json/pdmvserv_task_MUO-RunIIFall18wmLHEGS-00001__v1_T_180914_194042_3213"]).rstrip()#

                        import os
                        myOut = os.popen("curl -s -L --cookie  cookies/cookieMon.txt  --cookie-jar  cookies/cookieMon.txt  https://cms-gwmsmon.cern.ch/prodview/json/"+kn['name']).readlines()
                        import json
                        if(len(myOut)>0):
                            #print myOut[0]
                            try:
                                myOut = json.loads(myOut[0])
                                Running = myOut['Running']
                                Idle    = myOut['Idle']
                                runWath = 'https://cms-gwmsmon.cern.ch/prodview/'+kn['name']
                                RunIdle.append((runWath, Running, Idle))
                            except Exception: 
                                pass
                            #print 'HOLKA', myOut['Running'], myOut['Idle']


                        #import sys
                        #sys.exit()
                #n = '<a href="https://cms-gwmsmon.cern.ch/prodview/'+gs['reqmgr_name'][-1]['name']+'">i</a>'

                

                if runStat == []:
                    runStat = '-'
                rs = runStat[0].upper() if len(runStat) > 0 else ''
                rsSpan = '<span title="'+runStat+'">'+rs+'</span>'

                print '<td rowspan="'+str(prLen)+'" >'+priority+'</td>'

                if rs == 'D':
                    print '<td rowspan="'+str(prLen)+'"  class="withBGdone" style="background-size:100%">'+rsSpan+'</td>'
                elif rs == 'R' and runStat == 'running':
                    print '<td rowspan="'+str(prLen)+'"  class="withBG" style="background-size:100%">'+rsSpan+'</td>'
                elif rs == 'V':
                    print '<td rowspan="'+str(prLen)+'"  class="withBGval" style="background-size:100%">'+rsSpan+'</td>'
                else:
                    print '<td rowspan="'+str(prLen)+'" >'+rsSpan+'</td>'

                RunIdle = sorted(RunIdle, key=lambda it:-it[1])[:2]
                content = ''
                for RI in RunIdle:
                    content+= '<a  href="'+RI[0]+'">'+ str(RI[1])+'/'+str(RI[2]) +' </a>'
                print '<td align=\"center\" rowspan="'+str(prLen)+'" >',content, '</td>'

                #print getStatusTab(gs, prLen)

            if  gsMult[gs['prepid']] >= 1:
                nGS = gsMult[gs['prepid']]
                print getStatusTab(gs,nGS)
                gsMult[gs['prepid']] = 0

            if  drMult[chId] >= 1:
                nDR = drMult[chId]
                print getStatusTab(dr,nDR)
                #drMult[dr['prepid']] = 0

            #print getStatusTab(reReco)
            print getStatusTab(mini)
            print getStatusTab(nano)
            if reReco != None:
                print getStatusTab(reReco)
            print '</tr>'
            #print dn, getStatus(gs), getStatus(dr), getStatus(mini), getStatus(nano)

print '</table>'
print '</html>'

