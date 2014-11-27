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
options.register('mcGlobalTag', 'POSTLS172_V3::All',
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
options.register('useExplicitJTA', False,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.bool,
    "Use explicit jet-track association"
)
options.register('jetAlgo', 'AntiKt',
    VarParsing.multiplicity.singleton,
    VarParsing.varType.string,
    "Jet clustering algorithms (default is AntiKt)"
)
options.register('jetRadius', 0.8,
    VarParsing.multiplicity.singleton,
    VarParsing.varType.float,
    "Distance parameter R for jet clustering (default is 0.8)"
)
options.register('useSVClustering', True,
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
inputJetCorrLabelAK4 = ('AK4PFchs', ['L1FastJet', 'L2Relative', 'L3Absolute'], 'None')
inputJetCorrLabelAK7 = ('AK7PFchs', ['L1FastJet', 'L2Relative', 'L3Absolute'], 'None')

if not options.usePFchs:
    inputJetCorrLabelAK4 = ('AK4PF', ['L1FastJet', 'L2Relative', 'L3Absolute'], 'None')
    inputJetCorrLabelAK7 = ('AK7PF', ['L1FastJet', 'L2Relative', 'L3Absolute'], 'None')

if options.runOnData:
    inputJetCorrLabelAK4[1].append('L2L3Residual')
    inputJetCorrLabelAK7[1].append('L2L3Residual')

## b tagging
bTagInfos = ['impactParameterTagInfos','secondaryVertexTagInfos','inclusiveSecondaryVertexFinderTagInfos']
             #,'inclusiveSecondaryVertexFinderFilteredTagInfos','softMuonTagInfos','secondaryVertexNegativeTagInfos']
bTagDiscriminators = ['jetProbabilityBJetTags','jetBProbabilityBJetTags','combinedSecondaryVertexBJetTags','combinedInclusiveSecondaryVertexV2BJetTags']
                      #,'trackCountingHighPurBJetTags','trackCountingHighEffBJetTags'
                      #,'simpleSecondaryVertexHighPurBJetTags','simpleSecondaryVertexHighEffBJetTags'
                      #,'combinedInclusiveSecondaryVertexBJetTags'
                      #,'simpleInclusiveSecondaryVertexHighEffBJetTags','simpleInclusiveSecondaryVertexHighPurBJetTags'
                      #,'doubleSecondaryVertexHighEffBJetTags']

## Clustering algorithm label
algoLabel = 'CA'
if options.jetAlgo == 'AntiKt':
    algoLabel = 'AK'

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
#process.GlobalTag.globaltag = globalTag + '::All'
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:run2_mc')

#-------------------------------------
## Load calibration record for CSVV2
process.load('CondCore.DBCommon.CondDBSetup_cfi')
process.BTauMVAJetTagComputerRecord = cms.ESSource('PoolDBESSource',
    process.CondDBSetup,
    timetype = cms.string('runnumber'),
    toGet = cms.VPSet(cms.PSet(
        record = cms.string('BTauGenericMVAJetTagComputerRcd'),
        tag = cms.string('MVAComputerContainer_53X_JetTags_v3')
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
        '/store/relval/CMSSW_7_2_0_pre7/RelValProdTTbar/AODSIM/PRE_STA72_V4-v1/00000/3E58BB46-BD4B-E411-B2EC-002618943856.root'
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
jetAlgo="AK4"
usePF2PAT(process,runPF2PAT=True, jetAlgo=jetAlgo, runOnMC=not options.runOnData, postfix=postfix,
          jetCorrections=inputJetCorrLabelAK4, pvCollection=cms.InputTag('goodOfflinePrimaryVertices'+postfix))

## Top projections in PF2PAT
getattr(process,"pfPileUpJME"+postfix).checkClosestZVertex = False
getattr(process,"pfNoPileUpJME"+postfix).enable = options.usePFchs
getattr(process,"pfNoMuonJME"+postfix).enable = True
getattr(process,"pfNoElectronJME"+postfix).enable = True
getattr(process,"pfNoTau"+postfix).enable = False
getattr(process,"pfNoJet"+postfix).enable = True

#-------------------------------------
## Fat jets (Gen and Reco)
from RecoJets.JetProducers.ca4GenJets_cfi import ca4GenJets
process.genJetsNoNu = ca4GenJets.clone(
    jetAlgorithm = cms.string(options.jetAlgo),
    rParam = cms.double(options.jetRadius),
    src = cms.InputTag("genParticlesForJetsNoNu"+postfix)
)
from RecoJets.JetProducers.ca4PFJets_cfi import ca4PFJets
process.PFJetsCHS = ca4PFJets.clone(
    jetAlgorithm = cms.string(options.jetAlgo),
    rParam = cms.double(options.jetRadius),
    src = getattr(process,"pfJets"+postfix).src,
    srcPVs = getattr(process,"pfJets"+postfix).srcPVs,
    doAreaFastjet = getattr(process,"pfJets"+postfix).doAreaFastjet,
    jetPtMin = cms.double(20.)
)
## Filtered fat jets (Gen and Reco) (each module produces two jet collections, fat jets and subjets)
from RecoJets.JetProducers.ca4GenJets_cfi import ca4GenJets
process.genJetsNoNuFiltered = ca4GenJets.clone(
    jetAlgorithm = cms.string(options.jetAlgo),
    rParam = cms.double(options.jetRadius),
    src = cms.InputTag("genParticlesForJetsNoNu"+postfix),
    useFiltering = cms.bool(True),
    nFilt = cms.int32(3),
    rFilt = cms.double(0.3),
    writeCompound = cms.bool(True),
    jetCollInstanceName=cms.string("SubJets")
)
from RecoJets.JetProducers.ak5PFJetsFiltered_cfi import ak5PFJetsFiltered
process.PFJetsCHSFiltered = ak5PFJetsFiltered.clone(
    jetAlgorithm = cms.string(options.jetAlgo),
    rParam = cms.double(options.jetRadius),
    src = getattr(process,"pfJets"+postfix).src,
    srcPVs = getattr(process,"pfJets"+postfix).srcPVs,
    doAreaFastjet = getattr(process,"pfJets"+postfix).doAreaFastjet,
    writeCompound = cms.bool(True),
    jetCollInstanceName=cms.string("SubJets"),
    jetPtMin = cms.double(20.)
)
## MassDrop-BDRS filtered fat jets (Gen and Reco) (each module produces two jet collections, fat jets and subjets)
## Compared to the above filtered jets, here dynamic filtering radius is used (as in arXiv:0802.2470)
from RecoJets.JetProducers.ca4GenJets_cfi import ca4GenJets
process.genJetsNoNuMDBDRSFiltered = ca4GenJets.clone(
    jetAlgorithm = cms.string(options.jetAlgo),
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
process.PFJetsCHSMDBDRSFiltered = ak5PFJetsMassDropFiltered.clone(
    jetAlgorithm = cms.string(options.jetAlgo),
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
## Pruned fat jets (Gen and Reco) (each module produces two jet collections, fat jets and subjets)
from RecoJets.JetProducers.SubJetParameters_cfi import SubJetParameters
process.genJetsNoNuPruned = ca4GenJets.clone(
    SubJetParameters,
    jetAlgorithm = cms.string(options.jetAlgo),
    rParam = cms.double(options.jetRadius),
    src = cms.InputTag("genParticlesForJetsNoNu"+postfix),
    usePruning = cms.bool(True),
    writeCompound = cms.bool(True),
    jetCollInstanceName=cms.string("SubJets")
)
from RecoJets.JetProducers.ak5PFJetsPruned_cfi import ak5PFJetsPruned
process.PFJetsCHSPruned = ak5PFJetsPruned.clone(
    jetAlgorithm = cms.string(options.jetAlgo),
    rParam = cms.double(options.jetRadius),
    src = getattr(process,"pfJets"+postfix).src,
    srcPVs = getattr(process,"pfJets"+postfix).srcPVs,
    doAreaFastjet = getattr(process,"pfJets"+postfix).doAreaFastjet,
    writeCompound = cms.bool(True),
    jetCollInstanceName=cms.string("SubJets"),
    jetPtMin = cms.double(20.)
)
## Fat jets with Kt subjets (Gen and Reco) (each module produces two jet collections, fat jets and subjets)
## Kt subjets produced using Kt-based pruning with very loose pruning cuts (pruning is effectively disabled)
process.genJetsNoNuKtPruned = ca4GenJets.clone(
    SubJetParameters.clone(
        zcut = cms.double(0.),
        rcut_factor = cms.double(9999.)
    ),
    jetAlgorithm = cms.string(options.jetAlgo),
    rParam = cms.double(options.jetRadius),
    src = cms.InputTag("genParticlesForJetsNoNu"+postfix),
    usePruning = cms.bool(True),
    useKtPruning = cms.bool(True),
    writeCompound = cms.bool(True),
    jetCollInstanceName=cms.string("SubJets")
)
from RecoJets.JetProducers.ak5PFJetsPruned_cfi import ak5PFJetsPruned
process.PFJetsCHSKtPruned = ak5PFJetsPruned.clone(
    jetAlgorithm = cms.string(options.jetAlgo),
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
## Trimmed fat jets (Reco only)
from RecoJets.JetProducers.ak5PFJetsTrimmed_cfi import ak5PFJetsTrimmed
process.PFJetsCHSTrimmed = ak5PFJetsTrimmed.clone(
    jetAlgorithm = cms.string(options.jetAlgo),
    rParam = cms.double(options.jetRadius),
    src = getattr(process,"pfJets"+postfix).src,
    srcPVs = getattr(process,"pfJets"+postfix).srcPVs,
    doAreaFastjet = getattr(process,"pfJets"+postfix).doAreaFastjet,
    jetPtMin = cms.double(20.)
)

#-------------------------------------
## PATify the above jets
from PhysicsTools.PatAlgos.tools.jetTools import *
## Fat jets
switchJetCollection(process,
    jetSource=cms.InputTag('PFJetsCHS'),
    algo=algoLabel,
    rParam=options.jetRadius,
    btagInfos=bTagInfos,
    btagDiscriminators=bTagDiscriminators,
    jetCorrections = inputJetCorrLabelAK4,
    genJetCollection = cms.InputTag("genJetsNoNu"),
    explicitJTA=options.useExplicitJTA,
    postfix = postfix
)
## Filtered fat jets
addJetCollection(process,
    jetSource=cms.InputTag('PFJetsCHSFiltered'),
    algo=algoLabel,
    labelName='FilteredPFCHS',
    getJetMCFlavour=False,
    btagInfos=['None'],
    btagDiscriminators=['None'],
    jetCorrections=inputJetCorrLabelAK7,
    genJetCollection=cms.InputTag("genJetsNoNu"),
    postfix = postfix
)
## Filtered subjets of fat jets
addJetCollection(process,
    jetSource=cms.InputTag('PFJetsCHSFiltered','SubJets'),
    algo=algoLabel,
    labelName='FilteredSubjetsPFCHS',
    rParam=options.jetRadius,
    btagInfos=bTagInfos,
    btagDiscriminators=bTagDiscriminators,
    jetCorrections=inputJetCorrLabelAK4,
    genJetCollection=cms.InputTag('genJetsNoNuFiltered','SubJets'),
    explicitJTA=True,
    svClustering=options.useSVClustering,
    fatJets=cms.InputTag('PFJetsCHS'),
    groomedFatJets=cms.InputTag('PFJetsCHSFiltered'),
    postfix = postfix
)
### MassDrop-BDRS filtered fat jets
#addJetCollection(process,
    #jetSource=cms.InputTag('PFJetsCHSMDBDRSFiltered'),
    #algo=algoLabel,
    #labelName='MDBDRSFilteredPFCHS',
    #getJetMCFlavour=False,
    #btagInfos=['None'],
    #btagDiscriminators=['None'],
    #jetCorrections=inputJetCorrLabelAK7,
    #genJetCollection=cms.InputTag("genJetsNoNu"),
    #postfix = postfix
#)
### MassDrop-BDRS filtered subjets of fat jets
#addJetCollection(process,
    #jetSource=cms.InputTag('PFJetsCHSMDBDRSFiltered','SubJets'),
    #algo=algoLabel,
    #labelName='MDBDRSFilteredSubjetsPFCHS',
    #rParam=options.jetRadius,
    #btagInfos=bTagInfos,
    #btagDiscriminators=bTagDiscriminators,
    #jetCorrections=inputJetCorrLabelAK4,
    #genJetCollection=cms.InputTag('genJetsNoNuMDBDRSFiltered','SubJets'),
    #explicitJTA=True,
    #svClustering=options.useSVClustering,
    #fatJets=cms.InputTag('PFJetsCHS'),
    #groomedFatJets=cms.InputTag('PFJetsCHSMDBDRSFiltered'),
    #postfix = postfix
#)
## Pruned fat jets
addJetCollection(process,
    jetSource=cms.InputTag('PFJetsCHSPruned'),
    algo=algoLabel,
    labelName='PrunedPFCHS',
    getJetMCFlavour=False,
    btagInfos=['None'],
    btagDiscriminators=['None'],
    jetCorrections=inputJetCorrLabelAK7,
    genJetCollection=cms.InputTag("genJetsNoNu"),
    postfix = postfix
)
## Pruned subjets of fat jets
addJetCollection(process,
    jetSource=cms.InputTag('PFJetsCHSPruned','SubJets'),
    algo=algoLabel,
    labelName='PrunedSubjetsPFCHS',
    rParam=options.jetRadius,
    btagInfos=bTagInfos,
    btagDiscriminators=bTagDiscriminators,
    jetCorrections=inputJetCorrLabelAK4,
    genJetCollection=cms.InputTag('genJetsNoNuPruned','SubJets'),
    explicitJTA=True,
    svClustering=options.useSVClustering,
    fatJets=cms.InputTag('PFJetsCHS'),
    groomedFatJets=cms.InputTag('PFJetsCHSPruned'),
    postfix = postfix
)
## Kt pruned fat jets
addJetCollection(process,
    jetSource=cms.InputTag('PFJetsCHSKtPruned'),
    algo=algoLabel,
    labelName='KtPrunedPFCHS',
    getJetMCFlavour=False,
    btagInfos=['None'],
    btagDiscriminators=['None'],
    jetCorrections=inputJetCorrLabelAK7,
    genJetCollection=cms.InputTag("genJetsNoNu"),
    postfix = postfix
)
## Kt subjets of fat jets
addJetCollection(process,
    jetSource=cms.InputTag('PFJetsCHSKtPruned','SubJets'),
    algo=algoLabel,
    labelName='KtSubjetsPFCHS',
    rParam=options.jetRadius,
    btagInfos=bTagInfos,
    btagDiscriminators=bTagDiscriminators,
    jetCorrections=inputJetCorrLabelAK4,
    genJetCollection=cms.InputTag('genJetsNoNuKtPruned','SubJets'),
    explicitJTA=True,
    svClustering=options.useSVClustering,
    fatJets=cms.InputTag('PFJetsCHS'),
    groomedFatJets=cms.InputTag('PFJetsCHSKtPruned'),
    postfix = postfix
)

#-------------------------------------
## N-subjettiness
from RecoJets.JetProducers.nJettinessAdder_cfi import Njettiness

process.Njettiness = Njettiness.clone(
    src = cms.InputTag("PFJetsCHS"),
    cone = cms.double(options.jetRadius)
)

getattr(process,'patJets'+postfix).userData.userFloats.src += ['Njettiness:tau1','Njettiness:tau2','Njettiness:tau3']

#-------------------------------------
## Grooming ValueMaps
from RecoJets.JetProducers.ca8PFJetsCHS_groomingValueMaps_cfi import ca8PFJetsCHSPrunedLinks

process.PFJetsCHSPrunedMass = ca8PFJetsCHSPrunedLinks.clone(
    src = cms.InputTag("PFJetsCHS"),
    matched = cms.InputTag("PFJetsCHSPruned"),
    distMax = cms.double(options.jetRadius),
    value = cms.string('mass')
)

process.PFJetsCHSFilteredMass = ca8PFJetsCHSPrunedLinks.clone(
    src = cms.InputTag("PFJetsCHS"),
    matched = cms.InputTag("PFJetsCHSFiltered"),
    distMax = cms.double(options.jetRadius),
    value = cms.string('mass')
)

process.PFJetsCHSTrimmedMass = ca8PFJetsCHSPrunedLinks.clone(
    src = cms.InputTag("PFJetsCHS"),
    matched = cms.InputTag("PFJetsCHSTrimmed"),
    distMax = cms.double(options.jetRadius),
    value = cms.string('mass')
)

process.PFJetsCHSPrunedPt = ca8PFJetsCHSPrunedLinks.clone(
    src = cms.InputTag("PFJetsCHS"),
    matched = cms.InputTag("PFJetsCHSPruned"),
    distMax = cms.double(options.jetRadius),
    value = cms.string('pt')
)

process.PFJetsCHSFilteredPt = ca8PFJetsCHSPrunedLinks.clone(
    src = cms.InputTag("PFJetsCHS"),
    matched = cms.InputTag("PFJetsCHSFiltered"),
    distMax = cms.double(options.jetRadius),
    value = cms.string('pt')
)

process.PFJetsCHSTrimmedPt = ca8PFJetsCHSPrunedLinks.clone(
    src = cms.InputTag("PFJetsCHS"),
    matched = cms.InputTag("PFJetsCHSTrimmed"),
    distMax = cms.double(options.jetRadius),
    value = cms.string('pt')
)

getattr(process,'patJets'+postfix).userData.userFloats.src += ['PFJetsCHSPrunedMass','PFJetsCHSFilteredMass','PFJetsCHSTrimmedMass','PFJetsCHSPrunedPt','PFJetsCHSFilteredPt','PFJetsCHSTrimmedPt']

#-------------------------------------
#if options.useSVClustering:
    ### Enable clustering-based jet-SV association for IVF vertices and fat jets (not really needed here since it is mostly intended for subjets)
    #setattr(process,'inclusiveSecondaryVertexFinderTagInfos'+postfix, getattr(process,'inclusiveSecondaryVertexFinderTagInfos'+postfix).clone(
        #useSVClustering = cms.bool(False),
        #useSVMomentum   = cms.bool(options.useSVMomentum), # otherwise using SV flight direction
        #jetAlgorithm    = cms.string(options.jetAlgo),
        #rParam          = cms.double(options.jetRadius),
        #ghostRescaling  = cms.double(1e-18)
    #))

#-------------------------------------
## Establish references between PATified fat jets and subjets using the BoostedJetMerger
process.selectedPatJetsFilteredPFCHSPacked = cms.EDProducer("BoostedJetMerger",
    jetSrc=cms.InputTag("selectedPatJetsFilteredPFCHS"+postfix),
    subjetSrc=cms.InputTag("selectedPatJetsFilteredSubjetsPFCHS"+postfix)
)

process.selectedPatJetsMDBDRSFilteredPFCHSPacked = cms.EDProducer("BoostedJetMerger",
    jetSrc=cms.InputTag("selectedPatJetsMDBDRSFilteredPFCHS"+postfix),
    subjetSrc=cms.InputTag("selectedPatJetsMDBDRSFilteredSubjetsPFCHS"+postfix)
)

process.selectedPatJetsPrunedPFCHSPacked = cms.EDProducer("BoostedJetMerger",
    jetSrc=cms.InputTag("selectedPatJetsPrunedPFCHS"+postfix),
    subjetSrc=cms.InputTag("selectedPatJetsPrunedSubjetsPFCHS"+postfix)
)

process.selectedPatJetsKtPrunedPFCHSPacked = cms.EDProducer("BoostedJetMerger",
    jetSrc=cms.InputTag("selectedPatJetsKtPrunedPFCHS"+postfix),
    subjetSrc=cms.InputTag("selectedPatJetsKtSubjetsPFCHS"+postfix)
)

## Define BoostedJetMerger sequence
process.jetMergerSeq = cms.Sequence(
    process.selectedPatJetsFilteredPFCHSPacked
    #+ process.selectedPatJetsMDBDRSFilteredPFCHSPacked
    + process.selectedPatJetsPrunedPFCHSPacked
    + process.selectedPatJetsKtPrunedPFCHSPacked
)

#-------------------------------------
from PhysicsTools.PatAlgos.tools.coreTools import *
## Remove MC matching when running over data
if options.runOnData:
    removeMCMatching( process, ['All'] )

#-------------------------------------
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
## Adapt primary vertex collection
from PhysicsTools.PatAlgos.tools.pfTools import *
adaptPVs(process, pvCollection=cms.InputTag('goodOfflinePrimaryVertices'+postfix))

#-------------------------------------
## Add full JetFlavourInfo and TagInfos to PAT jets
for m in ['patJets'+postfix, 'patJetsFilteredSubjetsPFCHS'+postfix, 'patJetsMDBDRSFilteredSubjetsPFCHS'+postfix, 'patJetsKtBDRSFilteredSubjetsPFCHS'+postfix,
          'patJetsPrunedSubjetsPFCHS'+postfix, 'patJetsKtSubjetsPFCHS'+postfix]:
    if hasattr(process,m) and getattr( getattr(process,m), 'addBTagInfo' ):
        print "Switching 'addTagInfos' for " + m + " to 'True'"
        setattr( getattr(process,m), 'addTagInfos', cms.bool(True) )
    if hasattr(process,m):
        print "Switching 'addJetFlavourInfo' for " + m + " to 'True'"
        setattr( getattr(process,m), 'addJetFlavourInfo', cms.bool(True) )

#-------------------------------------
## Adapt fat jet b tagging
# Set the cone size for the jet-track association to the jet radius
getattr(process,'jetTracksAssociatorAtVertex'+postfix).coneSize = cms.double(options.jetRadius) # default is 0.5
getattr(process,'secondaryVertexTagInfos'+postfix).trackSelection.jetDeltaRMax = cms.double(options.jetRadius)   # default is 0.3
getattr(process,'secondaryVertexTagInfos'+postfix).vertexCuts.maxDeltaRToJetAxis = cms.double(options.jetRadius) # default is 0.5
# Set the jet-SV dR to the jet radius
getattr(process,'inclusiveSecondaryVertexFinderTagInfos'+postfix).vertexCuts.maxDeltaRToJetAxis = cms.double(options.jetRadius) # default is 0.5
getattr(process,'inclusiveSecondaryVertexFinderTagInfos'+postfix).extSVDeltaRToJet = cms.double(options.jetRadius) # default is 0.3
# Set the JP track dR cut to the jet radius
process.jetProbabilityComputerFat = process.jetProbabilityComputer.clone( deltaR = cms.double(options.jetRadius) ) # default is 0.3
getattr(process,'jetProbabilityBJetTags'+postfix).jetTagComputer = cms.string('jetProbabilityComputerFat')
# Set the JBP track dR cut to the jet radius
process.jetBProbabilityComputerFat = process.jetBProbabilityComputer.clone( deltaR = cms.double(options.jetRadius) ) # default is 0.5
getattr(process,'jetBProbabilityBJetTags'+postfix).jetTagComputer = cms.string('jetBProbabilityComputerFat')
# Set the CSV track dR cut to the jet radius
process.combinedSecondaryVertexComputerFat = process.combinedSecondaryVertexComputer.clone()
process.combinedSecondaryVertexComputerFat.trackSelection.jetDeltaRMax = cms.double(options.jetRadius) # default is 0.3
process.combinedSecondaryVertexComputerFat.trackPseudoSelection.jetDeltaRMax = cms.double(options.jetRadius) # default is 0.3
getattr(process,'combinedSecondaryVertexBJetTags'+postfix).jetTagComputer = cms.string('combinedSecondaryVertexComputerFat')
# Set the CSVV2 track dR cut to the jet radius
process.combinedSecondaryVertexV2ComputerFat = process.combinedSecondaryVertexV2Computer.clone()
process.combinedSecondaryVertexV2ComputerFat.trackSelection.jetDeltaRMax = cms.double(options.jetRadius) # default is 0.3
process.combinedSecondaryVertexV2ComputerFat.trackPseudoSelection.jetDeltaRMax = cms.double(options.jetRadius) # default is 0.3
getattr(process,'combinedInclusiveSecondaryVertexV2BJetTags'+postfix).jetTagComputer = cms.string('combinedSecondaryVertexV2ComputerFat')

#-------------------------------------
## Path definition
process.p = cms.Path(
    process.primaryVertexFilter
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
