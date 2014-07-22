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
options.register('mcGlobalTag', 'POSTLS170_V7',
    VarParsing.multiplicity.singleton,
    VarParsing.varType.string,
    "MC global tag"
)
options.register('dataGlobalTag', 'GR_70_V2_AN1',
    VarParsing.multiplicity.singleton,
    VarParsing.varType.string,
    "Data global tag"
)
options.register('outFilename', 'outfile',
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
options.register('doJTA', True,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Run jet-track association"
)
options.register('useExplicitJTA', False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Use explicit jet-track association"
)
options.register('doBTagging', True,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Run b tagging"
)
options.register('jetRadius', 0.8,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.float,
    "Distance parameter R for jet clustering (default is 0.8)"
)
options.register('useSVClustering', False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Use SV clustering"
)
options.register('useSVMomentum', False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Use SV momentum"
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
inputJetCorrLabelAK5 = ('AK5PFchs', ['L1FastJet', 'L2Relative', 'L3Absolute'], 'None')
inputJetCorrLabelAK7 = ('AK7PFchs', ['L1FastJet', 'L2Relative', 'L3Absolute'], 'None')

if not options.usePFchs:
    inputJetCorrLabelAK5 = ('AK5PF', ['L1FastJet', 'L2Relative', 'L3Absolute'], 'None')
    inputJetCorrLabelAK7 = ('AK7PF', ['L1FastJet', 'L2Relative', 'L3Absolute'], 'None')

if options.runOnData:
    inputJetCorrLabelAK5[1].append('L2L3Residual')
    inputJetCorrLabelAK7[1].append('L2L3Residual')

## b tagging
bTagInfos = ['impactParameterTagInfos','secondaryVertexTagInfos','inclusiveSecondaryVertexFinderTagInfos']
             #,'inclusiveSecondaryVertexFinderFilteredTagInfos','softMuonTagInfos','secondaryVertexNegativeTagInfos']
bTagDiscriminators = ['jetProbabilityBJetTags','jetBProbabilityBJetTags','combinedSecondaryVertexBJetTags','combinedSecondaryVertexV2BJetTags']
                      #,'trackCountingHighPurBJetTags','trackCountingHighEffBJetTags'
                      #,'simpleSecondaryVertexHighPurBJetTags','simpleSecondaryVertexHighEffBJetTags'
                      #,'combinedInclusiveSecondaryVertexBJetTags'
                      #,'simpleInclusiveSecondaryVertexHighEffBJetTags','simpleInclusiveSecondaryVertexHighPurBJetTags'
                      #,'doubleSecondaryVertexHighEffBJetTags']

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

#-------------------------------------
## Load calibration record for CSVV2
process.load('CondCore.DBCommon.CondDBSetup_cfi')
process.BTauMVAJetTagComputerRecord = cms.ESSource('PoolDBESSource',
    process.CondDBSetup,
    timetype = cms.string('runnumber'),
    toGet = cms.VPSet(cms.PSet(
        record = cms.string('BTauGenericMVAJetTagComputerRcd'),
        tag = cms.string('MVAComputerContainer_53X_JetTags_v2')
    )),
    connect = cms.string('frontier://FrontierProd/CMS_COND_PAT_000'),
    BlobStreamerName = cms.untracked.string('TBufferBlobStreamingService')
)
process.es_prefer_BTauMVAJetTagComputerRecord = cms.ESPrefer('PoolDBESSource','BTauMVAJetTagComputerRecord')

#-------------------------------------
## Events to process
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(options.maxEvents) )

## Options and Output Report
process.options   = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(options.wantSummary),
    allowUnscheduled = cms.untracked.bool(True)
)

#-------------------------------------
## Input files
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        # /TTJets_MSDecaysCKM_central_Tune4C_13TeV-madgraph-tauola/Spring14dr-PU_S14_POSTLS170_V6-v1/AODSIM
        '/store/mc/Spring14dr/TTJets_MSDecaysCKM_central_Tune4C_13TeV-madgraph-tauola/AODSIM/PU_S14_POSTLS170_V6-v1/00000/00120F7A-84F5-E311-9FBE-002618943910.root'
    )
)

if options.runOnData:
    process.source.fileNames = [
        # /SingleMu/Run2012D-22Jan2013-v1/AOD
        '/store/data/Run2012D/SingleMu/AOD/22Jan2013-v1/10000/0449388F-D2A7-E211-BEED-E0CB4E55363D.root'
    ]

#-------------------------------------
outFilename = string.replace(options.outFilename,'.root','') + '_mc.root'
if options.runOnData :
    outFilename = string.replace(options.outFilename,'.root','') + '_data.root'

## Output file
process.TFileService = cms.Service("TFileService",
   fileName = cms.string(outFilename)
)
#-------------------------------------
## Standard PAT Configuration File
process.load("PhysicsTools.PatAlgos.patSequences_cff")

## Configure PAT to use PF2PAT instead of AOD sources
## this function will modify the PAT sequences.
from PhysicsTools.PatAlgos.tools.pfTools import *

## Output Module Configuration (expects a path 'p')
from PhysicsTools.PatAlgos.patEventContent_cff import patEventContent
process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string("test.root"),
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
getattr(process,"pfPileUpJME"+postfix).checkClosestZVertex = False
getattr(process,"pfNoPileUpJME"+postfix).enable = options.usePFchs
getattr(process,"pfNoMuonJME"+postfix).enable = True
getattr(process,"pfNoElectronJME"+postfix).enable = True
getattr(process,"pfNoTau"+postfix).enable = False
getattr(process,"pfNoJet"+postfix).enable = True

#-------------------------------------
## CA jets (Gen and Reco)
from RecoJets.JetProducers.ca4GenJets_cfi import ca4GenJets
process.caGenJetsNoNu = ca4GenJets.clone(
    rParam = cms.double(options.jetRadius),
    src = cms.InputTag("genParticlesForJetsNoNu"+postfix)
)
from RecoJets.JetProducers.ca4PFJets_cfi import ca4PFJets
process.caPFJetsCHS = ca4PFJets.clone(
    rParam = cms.double(options.jetRadius),
    src = getattr(process,"pfJets"+postfix).src,
    srcPVs = getattr(process,"pfJets"+postfix).srcPVs,
    doAreaFastjet = getattr(process,"pfJets"+postfix).doAreaFastjet,
    jetPtMin = cms.double(20.)
)
## CA filtered jets (Gen and Reco) (each module produces two jet collections, fat jets and subjets)
from RecoJets.JetProducers.ca4GenJets_cfi import ca4GenJets
process.caGenJetsNoNuFiltered = ca4GenJets.clone(
    rParam = cms.double(options.jetRadius),
    src = cms.InputTag("genParticlesForJetsNoNu"+postfix),
    useFiltering = cms.bool(True),
    nFilt = cms.int32(3),
    rFilt = cms.double(0.3),
    writeCompound = cms.bool(True),
    jetCollInstanceName=cms.string("SubJets")
)
from RecoJets.JetProducers.ak5PFJetsFiltered_cfi import ak5PFJetsFiltered
process.caPFJetsCHSFiltered = ak5PFJetsFiltered.clone(
    jetAlgorithm = cms.string("CambridgeAachen"),
    rParam = cms.double(options.jetRadius),
    src = getattr(process,"pfJets"+postfix).src,
    srcPVs = getattr(process,"pfJets"+postfix).srcPVs,
    doAreaFastjet = getattr(process,"pfJets"+postfix).doAreaFastjet,
    writeCompound = cms.bool(True),
    jetCollInstanceName=cms.string("SubJets"),
    jetPtMin = cms.double(20.)
)
## CA MassDrop-BDRS filtered jets (Gen and Reco) (each module produces two jet collections, fat jets and subjets)
## Compared to the above filtered jets, here dynamic filtering radius is used (as in arXiv:0802.2470)
from RecoJets.JetProducers.ca4GenJets_cfi import ca4GenJets
process.caGenJetsNoNuMDBDRSFiltered = ca4GenJets.clone(
    rParam = cms.double(options.jetRadius),
    src = cms.InputTag("genParticlesForJetsNoNu"+postfix),
    useMassDropTagger = cms.bool(True),
    muCut = cms.double(0.667),
    yCut = cms.double(0.08),
    useFiltering = cms.bool(True),
    useDynamicFiltering = cms.bool(True),
    nFilt = cms.int32(3),
    rFilt = cms.double(0.3),
    rFiltFactor = cms.double(0.5),
    writeCompound = cms.bool(True),
    jetCollInstanceName=cms.string("SubJets")
)
from RecoJets.JetProducers.ak5PFJetsFiltered_cfi import ak5PFJetsMassDropFiltered
process.caPFJetsCHSMDBDRSFiltered = ak5PFJetsMassDropFiltered.clone(
    jetAlgorithm = cms.string("CambridgeAachen"),
    rParam = cms.double(options.jetRadius),
    src = getattr(process,"pfJets"+postfix).src,
    srcPVs = getattr(process,"pfJets"+postfix).srcPVs,
    doAreaFastjet = getattr(process,"pfJets"+postfix).doAreaFastjet,
    writeCompound = cms.bool(True),
    jetCollInstanceName=cms.string("SubJets"),
    jetPtMin = cms.double(20.),
    useDynamicFiltering = cms.bool(True),
    rFiltFactor = cms.double(0.5)
)
## CA Kt-BDRS filtered jets (Gen and Reco) (each module produces two jet collections, fat jets and subjets)
## Compared to the above filtered jets, here dynamic filtering radius is used (as in arXiv:0802.2470)
## However, here the mass drop is replaced by finding two Kt subjets which then set the size of the filtering radius
from RecoJets.JetProducers.ca4GenJets_cfi import ca4GenJets
process.caGenJetsNoNuKtBDRSFiltered = ca4GenJets.clone(
    rParam = cms.double(options.jetRadius),
    src = cms.InputTag("genParticlesForJetsNoNu"+postfix),
    usePruning = cms.bool(True),
    useKtPruning = cms.bool(True),
    zcut = cms.double(0.),
    rcut_factor = cms.double(9999.),
    useFiltering = cms.bool(True),
    useDynamicFiltering = cms.bool(True),
    nFilt = cms.int32(3),
    rFilt = cms.double(0.3),
    rFiltFactor = cms.double(0.5),
    writeCompound = cms.bool(True),
    jetCollInstanceName=cms.string("SubJets")
)
from RecoJets.JetProducers.ak5PFJetsFiltered_cfi import ak5PFJetsFiltered
process.caPFJetsCHSKtBDRSFiltered = ak5PFJetsFiltered.clone(
    jetAlgorithm = cms.string("CambridgeAachen"),
    rParam = cms.double(options.jetRadius),
    src = getattr(process,"pfJets"+postfix).src,
    srcPVs = getattr(process,"pfJets"+postfix).srcPVs,
    doAreaFastjet = getattr(process,"pfJets"+postfix).doAreaFastjet,
    writeCompound = cms.bool(True),
    jetCollInstanceName=cms.string("SubJets"),
    jetPtMin = cms.double(20.),
    usePruning = cms.bool(True),
    useKtPruning = cms.bool(True),
    zcut = cms.double(0.),
    rcut_factor = cms.double(9999.),
    useDynamicFiltering = cms.bool(True),
    rFiltFactor = cms.double(0.5)
)
## CA pruned jets (Gen and Reco) (each module produces two jet collections, fat jets and subjets)
from RecoJets.JetProducers.SubJetParameters_cfi import SubJetParameters
process.caGenJetsNoNuPruned = ca4GenJets.clone(
    SubJetParameters,
    rParam = cms.double(options.jetRadius),
    src = cms.InputTag("genParticlesForJetsNoNu"+postfix),
    usePruning = cms.bool(True),
    writeCompound = cms.bool(True),
    jetCollInstanceName=cms.string("SubJets")
)
from RecoJets.JetProducers.ak5PFJetsPruned_cfi import ak5PFJetsPruned
process.caPFJetsCHSPruned = ak5PFJetsPruned.clone(
    jetAlgorithm = cms.string("CambridgeAachen"),
    rParam = cms.double(options.jetRadius),
    src = getattr(process,"pfJets"+postfix).src,
    srcPVs = getattr(process,"pfJets"+postfix).srcPVs,
    doAreaFastjet = getattr(process,"pfJets"+postfix).doAreaFastjet,
    writeCompound = cms.bool(True),
    jetCollInstanceName=cms.string("SubJets"),
    jetPtMin = cms.double(20.)
)
## CA jets with Kt subjets (Gen and Reco) (each module produces two jet collections, fat jets and subjets)
## Kt subjets produced using Kt-based pruning with very loose pruning cuts (pruning is effectively disabled)
process.caGenJetsNoNuKtPruned = ca4GenJets.clone(
    SubJetParameters.clone(
        zcut = cms.double(0.),
        rcut_factor = cms.double(9999.)
    ),
    rParam = cms.double(options.jetRadius),
    src = cms.InputTag("genParticlesForJetsNoNu"+postfix),
    usePruning = cms.bool(True),
    useKtPruning = cms.bool(True),
    writeCompound = cms.bool(True),
    jetCollInstanceName=cms.string("SubJets")
)
from RecoJets.JetProducers.ak5PFJetsPruned_cfi import ak5PFJetsPruned
process.caPFJetsCHSKtPruned = ak5PFJetsPruned.clone(
    jetAlgorithm = cms.string("CambridgeAachen"),
    rParam = cms.double(options.jetRadius),
    src = getattr(process,"pfJets"+postfix).src,
    srcPVs = getattr(process,"pfJets"+postfix).srcPVs,
    doAreaFastjet = getattr(process,"pfJets"+postfix).doAreaFastjet,
    writeCompound = cms.bool(True),
    jetCollInstanceName=cms.string("SubJets"),
    jetPtMin = cms.double(20.),
    useKtPruning = cms.bool(True),
    zcut = cms.double(0.),
    rcut_factor = cms.double(9999.)
)
## CA trimmed jets (Reco only)
from RecoJets.JetProducers.ak5PFJetsTrimmed_cfi import ak5PFJetsTrimmed
process.caPFJetsCHSTrimmed = ak5PFJetsTrimmed.clone(
    jetAlgorithm = cms.string("CambridgeAachen"),
    rParam = cms.double(options.jetRadius),
    src = getattr(process,"pfJets"+postfix).src,
    srcPVs = getattr(process,"pfJets"+postfix).srcPVs,
    doAreaFastjet = getattr(process,"pfJets"+postfix).doAreaFastjet,
    jetPtMin = cms.double(20.)
)

#-------------------------------------
## PATify the above jets
from PhysicsTools.PatAlgos.tools.jetTools import *
## CA jets
switchJetCollection(process,
    jetSource=cms.InputTag('caPFJetsCHS'),
    algo='CA',
    rParam = options.jetRadius,
    btagInfos=bTagInfos,
    btagDiscriminators=bTagDiscriminators,
    jetCorrections = inputJetCorrLabelAK5,
    genJetCollection = cms.InputTag("caGenJetsNoNu"),
    postfix = postfix
)
## Filtered CA jets
addJetCollection(process,
    jetSource=cms.InputTag('caPFJetsCHSFiltered'),
    algo='CA',
    labelName='CAFilteredPFCHS',
    getJetMCFlavour=False,
    btagInfos=['None'],
    btagDiscriminators=['None'],
    jetCorrections=inputJetCorrLabelAK7,
    genJetCollection=cms.InputTag("caGenJetsNoNu"),
    postfix = postfix
)
## Filtered subjets of CA jets
addJetCollection(process,
    jetSource=cms.InputTag('caPFJetsCHSFiltered','SubJets'),
    algo='CA',
    labelName='CAFilteredSubjetsPFCHS',
    rParam = options.jetRadius,
    btagInfos=bTagInfos,
    btagDiscriminators=bTagDiscriminators,
    jetCorrections=inputJetCorrLabelAK5,
    genJetCollection=cms.InputTag('caGenJetsNoNuFiltered','SubJets'),
    postfix = postfix
)
## MassDrop-BDRS filtered CA jets
addJetCollection(process,
    jetSource=cms.InputTag('caPFJetsCHSMDBDRSFiltered'),
    algo='CA',
    labelName='CAMDBDRSFilteredPFCHS',
    getJetMCFlavour=False,
    btagInfos=['None'],
    btagDiscriminators=['None'],
    jetCorrections=inputJetCorrLabelAK7,
    genJetCollection=cms.InputTag("caGenJetsNoNu"),
    postfix = postfix
)
## MassDrop-BDRS filtered subjets of CA jets
addJetCollection(process,
    jetSource=cms.InputTag('caPFJetsCHSMDBDRSFiltered','SubJets'),
    algo='CA',
    labelName='CAMDBDRSFilteredSubjetsPFCHS',
    rParam = options.jetRadius,
    btagInfos=bTagInfos,
    btagDiscriminators=bTagDiscriminators,
    jetCorrections=inputJetCorrLabelAK5,
    genJetCollection=cms.InputTag('caGenJetsNoNuMDBDRSFiltered','SubJets'),
    postfix = postfix
)
## Kt-BDRS filtered CA jets
addJetCollection(process,
    jetSource=cms.InputTag('caPFJetsCHSKtBDRSFiltered'),
    algo='CA',
    labelName='CAKtBDRSFilteredPFCHS',
    getJetMCFlavour=False,
    btagInfos=['None'],
    btagDiscriminators=['None'],
    jetCorrections=inputJetCorrLabelAK7,
    genJetCollection=cms.InputTag("caGenJetsNoNu"),
    postfix = postfix
)
## Kt-BDRS filtered subjets of CA jets
addJetCollection(process,
    jetSource=cms.InputTag('caPFJetsCHSKtBDRSFiltered','SubJets'),
    algo='CA',
    labelName='CAKtBDRSFilteredSubjetsPFCHS',
    rParam = options.jetRadius,
    btagInfos=bTagInfos,
    btagDiscriminators=bTagDiscriminators,
    jetCorrections=inputJetCorrLabelAK5,
    genJetCollection=cms.InputTag('caGenJetsNoNuKtBDRSFiltered','SubJets'),
    postfix = postfix
)
## Pruned CA jets
addJetCollection(process,
    jetSource=cms.InputTag('caPFJetsCHSPruned'),
    algo='CA',
    labelName='CAPrunedPFCHS',
    getJetMCFlavour=False,
    btagInfos=['None'],
    btagDiscriminators=['None'],
    jetCorrections=inputJetCorrLabelAK7,
    genJetCollection=cms.InputTag("caGenJetsNoNu"),
    postfix = postfix
)
## Pruned subjets of CA jets
addJetCollection(process,
    jetSource=cms.InputTag('caPFJetsCHSPruned','SubJets'),
    algo='CA',
    labelName='CAPrunedSubjetsPFCHS',
    rParam = options.jetRadius,
    btagInfos=bTagInfos,
    btagDiscriminators=bTagDiscriminators,
    jetCorrections=inputJetCorrLabelAK5,
    genJetCollection=cms.InputTag('caGenJetsNoNuPruned','SubJets'),
    postfix = postfix
)
## Kt pruned CA jets
addJetCollection(process,
    jetSource=cms.InputTag('caPFJetsCHSKtPruned'),
    algo='CA',
    labelName='CAKtPrunedPFCHS',
    getJetMCFlavour=False,
    btagInfos=['None'],
    btagDiscriminators=['None'],
    jetCorrections=inputJetCorrLabelAK7,
    genJetCollection=cms.InputTag("caGenJetsNoNu"),
    postfix = postfix
)
## Kt subjets of CA jets
addJetCollection(process,
    jetSource=cms.InputTag('caPFJetsCHSKtPruned','SubJets'),
    algo='CA',
    labelName='CAKtSubjetsPFCHS',
    rParam = options.jetRadius,
    btagInfos=bTagInfos,
    btagDiscriminators=bTagDiscriminators,
    jetCorrections=inputJetCorrLabelAK5,
    genJetCollection=cms.InputTag('caGenJetsNoNuKtPruned','SubJets'),
    postfix = postfix
)

#-------------------------------------
## N-subjettiness
from RecoJets.JetProducers.nJettinessAdder_cfi import Njettiness

process.NjettinessCA = Njettiness.clone(
    src = cms.InputTag("caPFJetsCHS"),
    cone = cms.double(options.jetRadius)
)

getattr(process,'patJets'+postfix).userData.userFloats.src += ['NjettinessCA:tau1','NjettinessCA:tau2','NjettinessCA:tau3']

#-------------------------------------
## Grooming ValueMaps
from RecoJets.JetProducers.ca8PFJetsCHS_groomingValueMaps_cfi import ca8PFJetsCHSPrunedLinks

process.caPFJetsCHSPrunedMass = ca8PFJetsCHSPrunedLinks.clone(
    src = cms.InputTag("caPFJetsCHS"),
    matched = cms.InputTag("caPFJetsCHSPruned"),
    distMax = cms.double(options.jetRadius),
    value = cms.string('mass')
)

process.caPFJetsCHSFilteredMass = ca8PFJetsCHSPrunedLinks.clone(
    src = cms.InputTag("caPFJetsCHS"),
    matched = cms.InputTag("caPFJetsCHSFiltered"),
    distMax = cms.double(options.jetRadius),
    value = cms.string('mass')
)

process.caPFJetsCHSTrimmedMass = ca8PFJetsCHSPrunedLinks.clone(
    src = cms.InputTag("caPFJetsCHS"),
    matched = cms.InputTag("caPFJetsCHSTrimmed"),
    distMax = cms.double(options.jetRadius),
    value = cms.string('mass')
)

getattr(process,'patJets'+postfix).userData.userFloats.src += ['caPFJetsCHSPrunedMass','caPFJetsCHSFilteredMass','caPFJetsCHSTrimmedMass']

#-------------------------------------
if options.useSVClustering:
    ## Enable clustering-based jet-SV association for IVF vertices and subjets of CA jets
    setattr(process,'inclusiveSecondaryVertexFinderTagInfosCAFilteredSubjetsPFCHS'+postfix, getattr(process,'inclusiveSecondaryVertexFinderTagInfosCAFilteredSubjetsPFCHS'+postfix).clone(
        useSVClustering = cms.bool(True),
        useSVMomentum   = cms.bool(options.useSVMomentum), # otherwise using SV flight direction
        jetAlgorithm    = cms.string("CambridgeAachen"),
        rParam          = cms.double(options.jetRadius),
        ghostRescaling  = cms.double(1e-18),
        fatJets         = cms.InputTag("caPFJetsCHS"),
        groomedFatJets   = cms.InputTag("caPFJetsCHSFiltered")
    ))
    setattr(process,'inclusiveSecondaryVertexFinderTagInfosCAMDBDRSFilteredSubjetsPFCHS'+postfix, getattr(process,'inclusiveSecondaryVertexFinderTagInfosCAMDBDRSFilteredSubjetsPFCHS'+postfix).clone(
        useSVClustering = cms.bool(True),
        useSVMomentum   = cms.bool(options.useSVMomentum), # otherwise using SV flight direction
        jetAlgorithm    = cms.string("CambridgeAachen"),
        rParam          = cms.double(options.jetRadius),
        ghostRescaling  = cms.double(1e-18),
        fatJets         = cms.InputTag("caPFJetsCHS"),
        groomedFatJets   = cms.InputTag("caPFJetsCHSMDBDRSFiltered")
    ))
    setattr(process,'inclusiveSecondaryVertexFinderTagInfosCAKtBDRSFilteredSubjetsPFCHS'+postfix, getattr(process,'inclusiveSecondaryVertexFinderTagInfosCAKtBDRSFilteredSubjetsPFCHS'+postfix).clone(
        useSVClustering = cms.bool(True),
        useSVMomentum   = cms.bool(options.useSVMomentum), # otherwise using SV flight direction
        jetAlgorithm    = cms.string("CambridgeAachen"),
        rParam          = cms.double(options.jetRadius),
        ghostRescaling  = cms.double(1e-18),
        fatJets         = cms.InputTag("caPFJetsCHS"),
        groomedFatJets   = cms.InputTag("caPFJetsCHSKtBDRSFiltered")
    ))
    setattr(process,'inclusiveSecondaryVertexFinderTagInfosCAPrunedSubjetsPFCHS'+postfix, getattr(process,'inclusiveSecondaryVertexFinderTagInfosCAPrunedSubjetsPFCHS'+postfix).clone(
        useSVClustering = cms.bool(True),
        useSVMomentum   = cms.bool(options.useSVMomentum), # otherwise using SV flight direction
        jetAlgorithm    = cms.string("CambridgeAachen"),
        rParam          = cms.double(options.jetRadius),
        ghostRescaling  = cms.double(1e-18),
        fatJets         = cms.InputTag("caPFJetsCHS"),
        groomedFatJets   = cms.InputTag("caPFJetsCHSPruned")
    ))
    setattr(process,'inclusiveSecondaryVertexFinderTagInfosCAKtSubjetsPFCHS'+postfix, getattr(process,'inclusiveSecondaryVertexFinderTagInfosCAKtSubjetsPFCHS'+postfix).clone(
        useSVClustering = cms.bool(True),
        useSVMomentum   = cms.bool(options.useSVMomentum), # otherwise using SV flight direction
        jetAlgorithm    = cms.string("CambridgeAachen"),
        rParam          = cms.double(options.jetRadius),
        ghostRescaling  = cms.double(1e-18),
        fatJets         = cms.InputTag("caPFJetsCHS"),
        groomedFatJets   = cms.InputTag("caPFJetsCHSKtPruned")
    ))

#-------------------------------------
## New jet flavor still requires some cfg-level adjustments for subjets until it is better integrated into PAT
## Adjust the jet flavor for CA filtered subjets
setattr(process,'patJetFlavourAssociationCAFilteredSubjetsPFCHS'+postfix, getattr(process,'patJetFlavourAssociation'+postfix).clone(
    groomedJets = cms.InputTag("caPFJetsCHSFiltered"),
    subjets = cms.InputTag("caPFJetsCHSFiltered", "SubJets")
))
getattr(process,'patJetsCAFilteredSubjetsPFCHS'+postfix).JetFlavourInfoSource = cms.InputTag("patJetFlavourAssociationCAFilteredSubjetsPFCHS"+postfix,"SubJets")
## Adjust the jet flavor for CA MassDrop-BDRS filtered subjets
setattr(process,'patJetFlavourAssociationCAMDBDRSFilteredSubjetsPFCHS'+postfix, getattr(process,'patJetFlavourAssociation'+postfix).clone(
    groomedJets = cms.InputTag("caPFJetsCHSMDBDRSFiltered"),
    subjets = cms.InputTag("caPFJetsCHSMDBDRSFiltered", "SubJets")
))
getattr(process,'patJetsCAMDBDRSFilteredSubjetsPFCHS'+postfix).JetFlavourInfoSource = cms.InputTag("patJetFlavourAssociationCAMDBDRSFilteredSubjetsPFCHS"+postfix,"SubJets")
## Adjust the jet flavor for CA Kt-BDRS filtered subjets
setattr(process,'patJetFlavourAssociationCAKtBDRSFilteredSubjetsPFCHS'+postfix, getattr(process,'patJetFlavourAssociation'+postfix).clone(
    groomedJets = cms.InputTag("caPFJetsCHSKtBDRSFiltered"),
    subjets = cms.InputTag("caPFJetsCHSKtBDRSFiltered", "SubJets")
))
getattr(process,'patJetsCAKtBDRSFilteredSubjetsPFCHS'+postfix).JetFlavourInfoSource = cms.InputTag("patJetFlavourAssociationCAKtBDRSFilteredSubjetsPFCHS"+postfix,"SubJets")
## Adjust the jet flavor for CA pruned subjets
setattr(process,'patJetFlavourAssociationCAPrunedSubjetsPFCHS'+postfix, getattr(process,'patJetFlavourAssociation'+postfix).clone(
    groomedJets = cms.InputTag("caPFJetsCHSPruned"),
    subjets = cms.InputTag("caPFJetsCHSPruned", "SubJets")
))
getattr(process,'patJetsCAPrunedSubjetsPFCHS'+postfix).JetFlavourInfoSource = cms.InputTag("patJetFlavourAssociationCAPrunedSubjetsPFCHS"+postfix,"SubJets")
## Adjust the jet flavor for CA Kt subjets
setattr(process,'patJetFlavourAssociationCAKtSubjetsPFCHS'+postfix, getattr(process,'patJetFlavourAssociation'+postfix).clone(
    groomedJets = cms.InputTag("caPFJetsCHSKtPruned"),
    subjets = cms.InputTag("caPFJetsCHSKtPruned", "SubJets")
))
getattr(process,'patJetsCAKtSubjetsPFCHS'+postfix).JetFlavourInfoSource = cms.InputTag("patJetFlavourAssociationCAKtSubjetsPFCHS"+postfix,"SubJets")

#-------------------------------------
## Establish references between PATified fat jets and subjets using the BoostedJetMerger
process.selectedPatJetsCAFilteredPFCHSPacked = cms.EDProducer("BoostedJetMerger",
    jetSrc=cms.InputTag("selectedPatJetsCAFilteredPFCHS"+postfix),
    subjetSrc=cms.InputTag("selectedPatJetsCAFilteredSubjetsPFCHS"+postfix)
)

process.selectedPatJetsCAMDBDRSFilteredPFCHSPacked = cms.EDProducer("BoostedJetMerger",
    jetSrc=cms.InputTag("selectedPatJetsCAMDBDRSFilteredPFCHS"+postfix),
    subjetSrc=cms.InputTag("selectedPatJetsCAMDBDRSFilteredSubjetsPFCHS"+postfix)
)

process.selectedPatJetsCAKtBDRSFilteredPFCHSPacked = cms.EDProducer("BoostedJetMerger",
    jetSrc=cms.InputTag("selectedPatJetsCAKtBDRSFilteredPFCHS"+postfix),
    subjetSrc=cms.InputTag("selectedPatJetsCAKtBDRSFilteredSubjetsPFCHS"+postfix)
)

process.selectedPatJetsCAPrunedPFCHSPacked = cms.EDProducer("BoostedJetMerger",
    jetSrc=cms.InputTag("selectedPatJetsCAPrunedPFCHS"+postfix),
    subjetSrc=cms.InputTag("selectedPatJetsCAPrunedSubjetsPFCHS"+postfix)
)

process.selectedPatJetsCAKtPrunedPFCHSPacked = cms.EDProducer("BoostedJetMerger",
    jetSrc=cms.InputTag("selectedPatJetsCAKtPrunedPFCHS"+postfix),
    subjetSrc=cms.InputTag("selectedPatJetsCAKtSubjetsPFCHS"+postfix)
)

## Define BoostedJetMerger sequence
process.jetMergerSeq = cms.Sequence(
    process.selectedPatJetsCAFilteredPFCHSPacked
    + process.selectedPatJetsCAMDBDRSFilteredPFCHSPacked
    + process.selectedPatJetsCAKtBDRSFilteredPFCHSPacked
    + process.selectedPatJetsCAPrunedPFCHSPacked
    + process.selectedPatJetsCAKtPrunedPFCHSPacked
)

#-------------------------------------
from PhysicsTools.PatAlgos.tools.coreTools import *
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
## Define your analyzer and/or ntuple maker
#process.myAnalyzer = ...

#process.myNtupleMaker = ...

#-------------------------------------
## If using explicit jet-track association
if options.useExplicitJTA:
    from RecoJets.JetAssociationProducers.ak5JTA_cff import ak5JetTracksAssociatorExplicit
    for m in process.producerNames().split(' '):
        if m.startswith('jetTracksAssociatorAtVertex'):
            print 'Switching ' + m + ' to explicit jet-track association'
            setattr( process, m, ak5JetTracksAssociatorExplicit.clone(jets = getattr(getattr(process,m),'jets')) )

#-------------------------------------
## Define jet sequences
process.genJetSeq = cms.Sequence(
    process.caGenJetsNoNu
    + process.caGenJetsNoNuFiltered
    + process.caGenJetsNoNuMDBDRSFiltered
    + process.caGenJetsNoNuKtBDRSFiltered
    + process.caGenJetsNoNuPruned
    + process.caGenJetsNoNuKtPruned
)
process.jetSeq = cms.Sequence(
    (
    process.caPFJetsCHS
    + process.caPFJetsCHSFiltered
    + process.caPFJetsCHSMDBDRSFiltered
    + process.caPFJetsCHSKtBDRSFiltered
    + process.caPFJetsCHSPruned
    + process.caPFJetsCHSKtPruned
    + process.caPFJetsCHSTrimmed
    )
    * (
    process.NjettinessCA
    + process.caPFJetsCHSFilteredMass
    + process.caPFJetsCHSPrunedMass
    + process.caPFJetsCHSTrimmedMass
    )
)

if not options.runOnData:
    process.jetSeq = cms.Sequence( process.genJetSeq + process.jetSeq )

#-------------------------------------
## Adapt primary vertex collection
from PhysicsTools.PatAlgos.tools.pfTools import *
adaptPVs(process, pvCollection=cms.InputTag('goodOfflinePrimaryVertices'))

#-------------------------------------
## Add full JetFlavourInfo and TagInfos to PAT jets
for m in ['patJets'+postfix, 'patJetsCAFilteredSubjetsPFCHS'+postfix, 'patJetsCAMDBDRSFilteredSubjetsPFCHS'+postfix,
          'patJetsCAKtBDRSFilteredSubjetsPFCHS'+postfix, 'patJetsCAPrunedSubjetsPFCHS'+postfix, 'patJetsCAKtSubjetsPFCHS'+postfix]:
    if hasattr(process,m) and getattr( getattr(process,m), 'addBTagInfo' ):
        print "Switching 'addTagInfos' for " + m + " to 'True'"
        setattr( getattr(process,m), 'addTagInfos', cms.bool(True) )
    if hasattr(process,m):
        print "Switching 'addJetFlavourInfo' for " + m + " to 'True'"
        setattr( getattr(process,m), 'addJetFlavourInfo', cms.bool(True) )

#-------------------------------------
## Adapt fat jet b tagging
if options.doBTagging:
    # Set the cone size for the jet-track association to the jet radius
    getattr(process,'jetTracksAssociatorAtVertex'+postfix).coneSize = cms.double(options.jetRadius) # default is 0.5
    getattr(process,'secondaryVertexTagInfos'+postfix).trackSelection.jetDeltaRMax = cms.double(options.jetRadius)   # default is 0.3
    getattr(process,'secondaryVertexTagInfos'+postfix).vertexCuts.maxDeltaRToJetAxis = cms.double(options.jetRadius) # default is 0.5
    # Set the jet-SV dR to the jet radius
    getattr(process,'inclusiveSecondaryVertexFinderTagInfos'+postfix).vertexCuts.maxDeltaRToJetAxis = cms.double(options.jetRadius) # default is 0.5
    getattr(process,'inclusiveSecondaryVertexFinderTagInfos'+postfix).extSVDeltaRToJet = cms.double(options.jetRadius) # default is 0.3
    # Set the JP track dR cut to the jet radius
    process.jetProbabilityCA = process.jetProbability.clone( deltaR = cms.double(options.jetRadius) ) # default is 0.3
    getattr(process,'jetProbabilityBJetTags'+postfix).jetTagComputer = cms.string('jetProbabilityCA')
    # Set the JBP track dR cut to the jet radius
    process.jetBProbabilityCA = process.jetBProbability.clone( deltaR = cms.double(options.jetRadius) ) # default is 0.5
    getattr(process,'jetBProbabilityBJetTags'+postfix).jetTagComputer = cms.string('jetBProbabilityCA')
    # Set the CSV track dR cut to the jet radius
    process.combinedSecondaryVertexCA = process.combinedSecondaryVertex.clone()
    process.combinedSecondaryVertexCA.trackSelection.jetDeltaRMax = cms.double(options.jetRadius) # default is 0.3
    process.combinedSecondaryVertexCA.trackPseudoSelection.jetDeltaRMax = cms.double(options.jetRadius) # default is 0.3
    getattr(process,'combinedSecondaryVertexBJetTags'+postfix).jetTagComputer = cms.string('combinedSecondaryVertexCA')
    # Set the CSVV2 track dR cut to the jet radius
    process.combinedSecondaryVertexV2CA = process.combinedSecondaryVertexV2.clone()
    process.combinedSecondaryVertexV2CA.trackSelection.jetDeltaRMax = cms.double(options.jetRadius) # default is 0.3
    process.combinedSecondaryVertexV2CA.trackPseudoSelection.jetDeltaRMax = cms.double(options.jetRadius) # default is 0.3
    getattr(process,'combinedSecondaryVertexV2BJetTags'+postfix).jetTagComputer = cms.string('combinedSecondaryVertexV2CA')

#-------------------------------------
## Path definition
process.p = cms.Path(
    process.primaryVertexFilter
    * process.goodOfflinePrimaryVertices
    * process.jetSeq
    * process.jetMergerSeq
    #* (
    #process.myAnalyzer
    #+ process.myNtupleMaker
    #)
)

## Delete output module
del process.out

## Schedule definition
process.schedule = cms.Schedule(process.p)
