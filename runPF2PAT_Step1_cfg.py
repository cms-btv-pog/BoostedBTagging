###############################
####### Parameters ############
###############################
from FWCore.ParameterSet.VarParsing import VarParsing
import string

options = VarParsing ('python')

options.register('runOnData', False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Run this on real data"
)
## Make sure correct global tags are used (please refer to https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideFrontierConditions)
options.register('mcGlobalTag', 'START53_V27',
    VarParsing.multiplicity.singleton,
    VarParsing.varType.string,
    "MC global tag"
)
options.register('dataGlobalTag', 'FT53_V21A_AN6',
    VarParsing.multiplicity.singleton,
    VarParsing.varType.string,
    "Data global tag"
)
options.register('outFilename', 'patTuple_PF2PAT',
    VarParsing.multiplicity.singleton,
    VarParsing.varType.string,
    "Output file name"
)
options.register('reportEvery', 10,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.int,
    "Report every N events (default is N=10)"
)
options.register('wantSummary', False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Print out trigger and timing summary"
)
options.register('usePFchs', True,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Use PFchs"
)

## 'maxEvents' is already registered by the Framework, changing default value
options.setDefault('maxEvents', 100)

options.parseArguments()

print "Running on data: %s"%('True' if options.runOnData else 'False')
print "Using PFchs: %s"%('True' if options.usePFchs else 'False')

## Global tag
globalTag = options.mcGlobalTag
if options.runOnData:
    globalTag = options.dataGlobalTag

## Jet energy corrections
inputJetCorrLabelAK5 = ('AK5PFchs', ['L1FastJet', 'L2Relative', 'L3Absolute'])
inputJetCorrLabelAK7 = ('AK7PFchs', ['L1FastJet', 'L2Relative', 'L3Absolute'])

if not options.usePFchs:
    inputJetCorrLabelAK5 = ('AK5PF', ['L1FastJet', 'L2Relative', 'L3Absolute'])
    inputJetCorrLabelAK7 = ('AK7PF', ['L1FastJet', 'L2Relative', 'L3Absolute'])

if options.runOnData:
    inputJetCorrLabelAK5[1].append('L2L3Residual')
    inputJetCorrLabelAK7[1].append('L2L3Residual')

## b tagging
bTagInfos = ['impactParameterTagInfos','secondaryVertexTagInfos']
             #,'inclusiveSecondaryVertexFinderTagInfos','inclusiveSecondaryVertexFinderFilteredTagInfos','softMuonTagInfos','softElectronTagInfos']
bTagDiscriminators = ['jetProbabilityBJetTags','combinedSecondaryVertexBJetTags']
                      #,'trackCountingHighPurBJetTags','trackCountingHighEffBJetTags','jetBProbabilityBJetTags'
                      #,'simpleSecondaryVertexHighPurBJetTags','simpleSecondaryVertexHighEffBJetTags'
                      #,'simpleInclusiveSecondaryVertexHighEffBJetTags','simpleInclusiveSecondaryVertexHighPurBJetTags',
                      #,'combinedInclusiveSecondaryVertexBJetTags','doubleSecondaryVertexHighEffBJetTags']

import FWCore.ParameterSet.Config as cms

process = cms.Process("PF2PAT")

## MessageLogger
process.load("FWCore.MessageLogger.MessageLogger_cfi")
############## IMPORTANT ########################################
# If you run over many samples and you save the log, remember to reduce
# the size of the output by prescaling the report of the event number
process.MessageLogger.cerr.FwkReport.reportEvery = options.reportEvery
process.MessageLogger.cerr.default.limit = 10
#################################################################

## Geometry and Detector Conditions
process.load("Configuration.Geometry.GeometryIdeal_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.GlobalTag.globaltag = globalTag + '::All'

## Events to process
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(options.maxEvents) )

## Options and Output Report
process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(options.wantSummary) )

#-------------------------------------
## Input files
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        # /TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7C-v1/AODSIM
        '/store/mc/Summer12_DR53X/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V7C-v1/00000/008BD264-1526-E211-897A-00266CFFA7BC.root'
    )
)

if options.runOnData:
    process.source.fileNames = [
        # /SingleMu/Run2012D-22Jan2013-v1/AOD
        '/store/data/Run2012D/SingleMu/AOD/22Jan2013-v1/10000/0449388F-D2A7-E211-BEED-E0CB4E55363D.root'
    ]

#-------------------------------------
## Standard PAT Configuration File
process.load("PhysicsTools.PatAlgos.patSequences_cff")

## Configure PAT to use PF2PAT instead of AOD sources
## this function will modify the PAT sequences.
from PhysicsTools.PatAlgos.tools.pfTools import *

outFilename = string.replace(options.outFilename,'.root','') + '_mc.root'
if options.runOnData :
    outFilename = string.replace(options.outFilename,'.root','') + '_data.root'

## Output Module Configuration (expects a path 'p')
from PhysicsTools.PatAlgos.patEventContent_cff import patEventContent
process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string(outFilename),
    # save only events passing the full path
    SelectEvents   = cms.untracked.PSet( SelectEvents = cms.vstring('p') ),
    # save PAT Layer 1 output; you need a '*' to
    # unpack the list of commands 'patEventContent'
    outputCommands = cms.untracked.vstring('drop *', *patEventContent)
)

postfix = "PFlow"
jetAlgo="AK5"
usePF2PAT(process,runPF2PAT=True, jetAlgo=jetAlgo, runOnMC=not options.runOnData, postfix=postfix,
          jetCorrections=inputJetCorrLabelAK5, pvCollection=cms.InputTag('goodOfflinePrimaryVertices'))

## Top projections in PF2PAT
getattr(process,"pfPileUp"+postfix).checkClosestZVertex = False
getattr(process,"pfNoPileUp"+postfix).enable = options.usePFchs
getattr(process,"pfNoMuon"+postfix).enable = True
getattr(process,"pfNoElectron"+postfix).enable = True
getattr(process,"pfNoTau"+postfix).enable = False
getattr(process,"pfNoJet"+postfix).enable = True

#-------------------------------------
from PhysicsTools.PatAlgos.tools.coreTools import *
## Remove taus from the PAT sequence
removeSpecificPATObjects(process,names=['Taus'],postfix=postfix)

## Remove MC matching when running over data
if options.runOnData:
    removeMCMatching( process, ['All'] )

#-------------------------------------
## Produce a collection of good primary vertices
from PhysicsTools.SelectorUtils.pvSelector_cfi import pvSelector
process.goodOfflinePrimaryVertices = cms.EDFilter("PrimaryVertexObjectFilter",
    filterParams = pvSelector.clone(
        minNdof = cms.double(4.0), # this is >= 4
        maxZ = cms.double(24.0),
        maxRho = cms.double(2.0)
    ),
    src = cms.InputTag('offlinePrimaryVertices')
)

## Good primary vertex event filter
process.primaryVertexFilter = cms.EDFilter('VertexSelector',
    src = cms.InputTag('offlinePrimaryVertices'),
    cut = cms.string('!isFake & ndof > 4 & abs(z) <= 24 & position.Rho <= 2'),
    filter = cms.bool(True)
)

#-------------------------------------
## Tweak output event content
from PhysicsTools.PatAlgos.patEventContent_cff import patEventContentNoCleaning
patEventContentNoCleaning.append('drop *_selectedPatPFParticlesPFlow_*_*')
patEventContentNoCleaning.append('drop *_selectedPatJetsPFlow_*_*')
patEventContentNoCleaning.append('keep GenEventInfoProduct_generator_*_*')
patEventContentNoCleaning.append('keep PileupSummaryInfos_*_*_*')
## GenParticles
patEventContentNoCleaning.append('keep recoGenParticles_genParticles_*_*')
## For PF jets
patEventContentNoCleaning.append('keep *_pfNoElectronPFlow_*_*')
patEventContentNoCleaning.append('keep *_kt6PFJets_rho_*')
## HLT trigger results
patEventContentNoCleaning.append('drop *_TriggerResults_*_*')
patEventContentNoCleaning.append('keep *_TriggerResults_*_HLT')
## For b tagging
patEventContentNoCleaning.append('keep *_offlineBeamSpot_*_*')
patEventContentNoCleaning.append('keep *_generalTracks_*_*')
patEventContentNoCleaning.append('keep *_offlinePrimaryVertices_*_*')
## For soft lepton taggers
patEventContentNoCleaning.append('keep recoMuons_muons_*_*')
patEventContentNoCleaning.append('keep recoTracks_globalMuons_*_*')
patEventContentNoCleaning.append('keep recoTracks_standAloneMuons_*_*')
patEventContentNoCleaning.append('keep *_gsfElectrons_*_*')
patEventContentNoCleaning.append('keep *_gsfElectronCores_*_*')
patEventContentNoCleaning.append('keep *_electronGsfTracks_*_*')

process.out.outputCommands = cms.untracked.vstring('drop *', *patEventContentNoCleaning)

#-------------------------------------
## Remove tau stuff that really shouldn't be there (probably a bug in PAT)
process.patDefaultSequencePFlow.remove(process.kt6PFJetsForRhoComputationVoronoiPFlow)
for m in getattr(process,"patDefaultSequence"+postfix).moduleNames():
    if m.startswith('hpsPFTau'):
        getattr(process,"patDefaultSequence"+postfix).remove(getattr(process,m))

#-------------------------------------
## Path definition
process.p = cms.Path(
    process.primaryVertexFilter
    * process.goodOfflinePrimaryVertices
    * getattr(process,"patPF2PATSequence"+postfix)
)

## Define Endpath
process.outpath = cms.EndPath(process.out)

## Schedule definition
process.schedule = cms.Schedule(process.p)
process.schedule.append(process.outpath)
