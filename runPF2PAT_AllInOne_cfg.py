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
bTagInfos = ['impactParameterTagInfos','secondaryVertexTagInfos','inclusiveSecondaryVertexFinderTagInfos']
             #,'inclusiveSecondaryVertexFinderFilteredTagInfos','softMuonTagInfos','secondaryVertexNegativeTagInfos']
bTagDiscriminators = ['jetProbabilityBJetTags','combinedSecondaryVertexBJetTags'
                      #,'trackCountingHighPurBJetTags','trackCountingHighEffBJetTags','jetBProbabilityBJetTags'
                      #,'simpleSecondaryVertexHighPurBJetTags','simpleSecondaryVertexHighEffBJetTags'
                      ,'combinedInclusiveSecondaryVertexBJetTags']
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
getattr(process,"pfPileUp"+postfix).checkClosestZVertex = False
getattr(process,"pfNoPileUp"+postfix).enable = options.usePFchs
getattr(process,"pfNoMuon"+postfix).enable = True
getattr(process,"pfNoElectron"+postfix).enable = True
getattr(process,"pfNoTau"+postfix).enable = False
getattr(process,"pfNoJet"+postfix).enable = True

#-------------------------------------
## CA8 jets (Gen and Reco)
from RecoJets.JetProducers.ca4GenJets_cfi import ca4GenJets
process.ca8GenJetsNoNu = ca4GenJets.clone(
    rParam = cms.double(0.8),
    src = cms.InputTag("genParticlesForJetsNoNu")
)
from RecoJets.JetProducers.ca4PFJets_cfi import ca4PFJets
process.ca8PFJetsCHS = ca4PFJets.clone(
    rParam = cms.double(0.8),
    src = getattr(process,"pfJets"+postfix).src,
    srcPVs = getattr(process,"pfJets"+postfix).srcPVs,
    doAreaFastjet = getattr(process,"pfJets"+postfix).doAreaFastjet,
    jetPtMin = cms.double(20.)
)
## CA8 filtered jets (Gen and Reco) (each module produces two jet collections, fat jets and subjets)
from RecoJets.JetProducers.ca4GenJets_cfi import ca4GenJets
process.ca8GenJetsNoNuFiltered = ca4GenJets.clone(
    rParam = cms.double(0.8),
    src = cms.InputTag("genParticlesForJetsNoNu"),
    useFiltering = cms.bool(True),
    nFilt = cms.int32(3),
    rFilt = cms.double(0.3),
    writeCompound = cms.bool(True),
    jetCollInstanceName=cms.string("SubJets")
)
from RecoJets.JetProducers.ak5PFJetsFiltered_cfi import ak5PFJetsFiltered
process.ca8PFJetsCHSFiltered = ak5PFJetsFiltered.clone(
    jetAlgorithm = cms.string("CambridgeAachen"),
    rParam = cms.double(0.8),
    src = getattr(process,"pfJets"+postfix).src,
    srcPVs = getattr(process,"pfJets"+postfix).srcPVs,
    doAreaFastjet = getattr(process,"pfJets"+postfix).doAreaFastjet,
    writeCompound = cms.bool(True),
    jetCollInstanceName=cms.string("SubJets"),
    jetPtMin = cms.double(20.)
)
## CA8 MassDrop-BDRS filtered jets (Gen and Reco) (each module produces two jet collections, fat jets and subjets)
## Compared to the above filtered jets, here dynamic filtering radius is used (as in arXiv:0802.2470)
from RecoJets.JetProducers.ca4GenJets_cfi import ca4GenJets
process.ca8GenJetsNoNuMDBDRSFiltered = ca4GenJets.clone(
    rParam = cms.double(0.8),
    src = cms.InputTag("genParticlesForJetsNoNu"),
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
process.ca8PFJetsCHSMDBDRSFiltered = ak5PFJetsMassDropFiltered.clone(
    jetAlgorithm = cms.string("CambridgeAachen"),
    rParam = cms.double(0.8),
    src = getattr(process,"pfJets"+postfix).src,
    srcPVs = getattr(process,"pfJets"+postfix).srcPVs,
    doAreaFastjet = getattr(process,"pfJets"+postfix).doAreaFastjet,
    writeCompound = cms.bool(True),
    jetCollInstanceName=cms.string("SubJets"),
    jetPtMin = cms.double(20.),
    useDynamicFiltering = cms.bool(True),
    rFiltFactor = cms.double(0.5)
)
## CA8 Kt-BDRS filtered jets (Gen and Reco) (each module produces two jet collections, fat jets and subjets)
## Compared to the above filtered jets, here dynamic filtering radius is used (as in arXiv:0802.2470)
## However, here the mass drop is replaced by finding two Kt subjets which then set the size of the filtering radius
from RecoJets.JetProducers.ca4GenJets_cfi import ca4GenJets
process.ca8GenJetsNoNuKtBDRSFiltered = ca4GenJets.clone(
    rParam = cms.double(0.8),
    src = cms.InputTag("genParticlesForJetsNoNu"),
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
process.ca8PFJetsCHSKtBDRSFiltered = ak5PFJetsFiltered.clone(
    jetAlgorithm = cms.string("CambridgeAachen"),
    rParam = cms.double(0.8),
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
## CA8 pruned jets (Gen and Reco) (each module produces two jet collections, fat jets and subjets)
from RecoJets.JetProducers.SubJetParameters_cfi import SubJetParameters
process.ca8GenJetsNoNuPruned = ca4GenJets.clone(
    SubJetParameters,
    rParam = cms.double(0.8),
    src = cms.InputTag("genParticlesForJetsNoNu"),
    usePruning = cms.bool(True),
    writeCompound = cms.bool(True),
    jetCollInstanceName=cms.string("SubJets")
)
from RecoJets.JetProducers.ak5PFJetsPruned_cfi import ak5PFJetsPruned
process.ca8PFJetsCHSPruned = ak5PFJetsPruned.clone(
    jetAlgorithm = cms.string("CambridgeAachen"),
    rParam = cms.double(0.8),
    src = getattr(process,"pfJets"+postfix).src,
    srcPVs = getattr(process,"pfJets"+postfix).srcPVs,
    doAreaFastjet = getattr(process,"pfJets"+postfix).doAreaFastjet,
    writeCompound = cms.bool(True),
    jetCollInstanceName=cms.string("SubJets"),
    jetPtMin = cms.double(20.)
)
## CA8 jets with Kt subjets (Gen and Reco) (each module produces two jet collections, fat jets and subjets)
## Kt subjets produced using Kt-based pruning with very loose pruning cuts (pruning is effectively disabled)
process.ca8GenJetsNoNuKtPruned = ca4GenJets.clone(
    SubJetParameters.clone(
        zcut = cms.double(0.),
        rcut_factor = cms.double(9999.)
    ),
    rParam = cms.double(0.8),
    src = cms.InputTag("genParticlesForJetsNoNu"),
    usePruning = cms.bool(True),
    useKtPruning = cms.bool(True),
    writeCompound = cms.bool(True),
    jetCollInstanceName=cms.string("SubJets")
)
from RecoJets.JetProducers.ak5PFJetsPruned_cfi import ak5PFJetsPruned
process.ca8PFJetsCHSKtPruned = ak5PFJetsPruned.clone(
    jetAlgorithm = cms.string("CambridgeAachen"),
    rParam = cms.double(0.8),
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
## CA8 trimmed jets (Reco only)
from RecoJets.JetProducers.ak5PFJetsTrimmed_cfi import ak5PFJetsTrimmed
process.ca8PFJetsCHSTrimmed = ak5PFJetsTrimmed.clone(
    jetAlgorithm = cms.string("CambridgeAachen"),
    rParam = cms.double(0.8),
    src = getattr(process,"pfJets"+postfix).src,
    srcPVs = getattr(process,"pfJets"+postfix).srcPVs,
    doAreaFastjet = getattr(process,"pfJets"+postfix).doAreaFastjet,
    jetPtMin = cms.double(20.)
)

#-------------------------------------
## PATify the above jets
from PhysicsTools.PatAlgos.tools.jetTools import *
## Default AK5 jets (switching done to run only specified b-tag algorithms)
switchJetCollection(process,
    cms.InputTag("pfNoTau"+postfix),
    jetIdLabel='ak5',
    rParam = 0.5,
    useLegacyFlavour=False,
    doJTA=options.doJTA,
    doBTagging=options.doBTagging,
    btagInfo=bTagInfos,
    btagdiscriminators=bTagDiscriminators,
    jetCorrLabel = inputJetCorrLabelAK5,
    doType1MET   = False,
    genJetCollection = cms.InputTag("ak5GenJetsNoNu"),
    doJetID      = False,
    postfix = postfix
)
## CA8 jets
switchJetCollection(process,
    cms.InputTag('ca8PFJetsCHS'),
    jetIdLabel='ca8',
    rParam = 0.8,
    useLegacyFlavour=False,
    doJTA=options.doJTA,
    doBTagging=options.doBTagging,
    btagInfo=bTagInfos,
    btagdiscriminators=bTagDiscriminators,
    jetCorrLabel = inputJetCorrLabelAK5,
    doType1MET   = False,
    genJetCollection = cms.InputTag("ca8GenJetsNoNu"),
    doJetID      = False,
)
## Filtered CA8 jets
addJetCollection(
    process,
    cms.InputTag('ca8PFJetsCHSFiltered'),
    'CA8','FilteredPFCHS',
    getJetMCFlavour=False,
    doJTA=False,
    doBTagging=False,
    btagInfo=bTagInfos,
    btagdiscriminators=bTagDiscriminators,
    jetCorrLabel=inputJetCorrLabelAK7,
    doType1MET=False,
    doL1Cleaning=False,
    doL1Counters=False,
    doJetID=False,
    genJetCollection=cms.InputTag("ca8GenJetsNoNu")
)
## Filtered subjets of CA8 jets
addJetCollection(
    process,
    cms.InputTag('ca8PFJetsCHSFiltered','SubJets'),
    'CA8', 'FilteredSubjetsPFCHS',
    rParam = 0.8,
    useLegacyFlavour=False,
    doJTA=options.doJTA,
    doBTagging=options.doBTagging,
    btagInfo=bTagInfos,
    btagdiscriminators=bTagDiscriminators,
    jetCorrLabel=inputJetCorrLabelAK5,
    doType1MET=False,
    doL1Cleaning=False,
    doL1Counters=False,
    doJetID=False,
    genJetCollection=cms.InputTag('ca8GenJetsNoNuFiltered','SubJets')
)
## MassDrop-BDRS filtered CA8 jets
addJetCollection(
    process,
    cms.InputTag('ca8PFJetsCHSMDBDRSFiltered'),
    'CA8','MDBDRSFilteredPFCHS',
    getJetMCFlavour=False,
    doJTA=False,
    doBTagging=False,
    btagInfo=bTagInfos,
    btagdiscriminators=bTagDiscriminators,
    jetCorrLabel=inputJetCorrLabelAK7,
    doType1MET=False,
    doL1Cleaning=False,
    doL1Counters=False,
    doJetID=False,
    genJetCollection=cms.InputTag("ca8GenJetsNoNu")
)
## MassDrop-BDRS filtered subjets of CA8 jets
addJetCollection(
    process,
    cms.InputTag('ca8PFJetsCHSMDBDRSFiltered','SubJets'),
    'CA8', 'MDBDRSFilteredSubjetsPFCHS',
    rParam = 0.8,
    useLegacyFlavour=False,
    doJTA=options.doJTA,
    doBTagging=options.doBTagging,
    btagInfo=bTagInfos,
    btagdiscriminators=bTagDiscriminators,
    jetCorrLabel=inputJetCorrLabelAK5,
    doType1MET=False,
    doL1Cleaning=False,
    doL1Counters=False,
    doJetID=False,
    genJetCollection=cms.InputTag('ca8GenJetsNoNuMDBDRSFiltered','SubJets')
)
## Kt-BDRS filtered CA8 jets
addJetCollection(
    process,
    cms.InputTag('ca8PFJetsCHSKtBDRSFiltered'),
    'CA8','KtBDRSFilteredPFCHS',
    getJetMCFlavour=False,
    doJTA=False,
    doBTagging=False,
    btagInfo=bTagInfos,
    btagdiscriminators=bTagDiscriminators,
    jetCorrLabel=inputJetCorrLabelAK7,
    doType1MET=False,
    doL1Cleaning=False,
    doL1Counters=False,
    doJetID=False,
    genJetCollection=cms.InputTag("ca8GenJetsNoNu")
)
## Kt-BDRS filtered subjets of CA8 jets
addJetCollection(
    process,
    cms.InputTag('ca8PFJetsCHSKtBDRSFiltered','SubJets'),
    'CA8', 'KtBDRSFilteredSubjetsPFCHS',
    rParam = 0.8,
    useLegacyFlavour=False,
    doJTA=options.doJTA,
    doBTagging=options.doBTagging,
    btagInfo=bTagInfos,
    btagdiscriminators=bTagDiscriminators,
    jetCorrLabel=inputJetCorrLabelAK5,
    doType1MET=False,
    doL1Cleaning=False,
    doL1Counters=False,
    doJetID=False,
    genJetCollection=cms.InputTag('ca8GenJetsNoNuKtBDRSFiltered','SubJets')
)
## Pruned CA8 jets
addJetCollection(
    process,
    cms.InputTag('ca8PFJetsCHSPruned'),
    'CA8','PrunedPFCHS',
    getJetMCFlavour=False,
    doJTA=False,
    doBTagging=False,
    btagInfo=bTagInfos,
    btagdiscriminators=bTagDiscriminators,
    jetCorrLabel=inputJetCorrLabelAK7,
    doType1MET=False,
    doL1Cleaning=False,
    doL1Counters=False,
    doJetID=False,
    genJetCollection=cms.InputTag("ca8GenJetsNoNu")
)
## Pruned subjets of CA8 jets
addJetCollection(
    process,
    cms.InputTag('ca8PFJetsCHSPruned','SubJets'),
    'CA8', 'PrunedSubjetsPFCHS',
    rParam = 0.8,
    useLegacyFlavour=False,
    doJTA=options.doJTA,
    doBTagging=options.doBTagging,
    btagInfo=bTagInfos,
    btagdiscriminators=bTagDiscriminators,
    jetCorrLabel=inputJetCorrLabelAK5,
    doType1MET=False,
    doL1Cleaning=False,
    doL1Counters=False,
    doJetID=False,
    genJetCollection=cms.InputTag('ca8GenJetsNoNuPruned','SubJets')
)
## Kt pruned CA8 jets
addJetCollection(
    process,
    cms.InputTag('ca8PFJetsCHSKtPruned'),
    'CA8','KtPrunedPFCHS',
    getJetMCFlavour=False,
    doJTA=False,
    doBTagging=False,
    btagInfo=bTagInfos,
    btagdiscriminators=bTagDiscriminators,
    jetCorrLabel=inputJetCorrLabelAK7,
    doType1MET=False,
    doL1Cleaning=False,
    doL1Counters=False,
    doJetID=False,
    genJetCollection=cms.InputTag("ca8GenJetsNoNu")
)
## Kt subjets of CA8 jets
addJetCollection(
    process,
    cms.InputTag('ca8PFJetsCHSKtPruned','SubJets'),
    'CA8', 'KtSubjetsPFCHS',
    rParam = 0.8,
    useLegacyFlavour=False,
    doJTA=options.doJTA,
    doBTagging=options.doBTagging,
    btagInfo=bTagInfos,
    btagdiscriminators=bTagDiscriminators,
    jetCorrLabel=inputJetCorrLabelAK5,
    doType1MET=False,
    doL1Cleaning=False,
    doL1Counters=False,
    doJetID=False,
    genJetCollection=cms.InputTag('ca8GenJetsNoNuKtPruned','SubJets')
)

#-------------------------------------
## N-subjettiness
from RecoJets.JetProducers.nJettinessAdder_cfi import Njettiness

process.NjettinessCA8 = Njettiness.clone(
    src = cms.InputTag("ca8PFJetsCHS"),
    cone = cms.double(0.8)
)

process.patJets.userData.userFloats.src += ['NjettinessCA8:tau1','NjettinessCA8:tau2','NjettinessCA8:tau3']

#-------------------------------------
## Grooming ValueMaps
from RecoJets.JetProducers.ca8PFJetsCHS_groomingValueMaps_cfi import ca8PFJetsCHSPrunedLinks

process.ca8PFJetsCHSPrunedMass = ca8PFJetsCHSPrunedLinks.clone(
    src = cms.InputTag("ca8PFJetsCHS"),
    matched = cms.InputTag("ca8PFJetsCHSPruned"),
    distMax = cms.double(0.8),
    value = cms.string('mass')
)

process.ca8PFJetsCHSFilteredMass = ca8PFJetsCHSPrunedLinks.clone(
    src = cms.InputTag("ca8PFJetsCHS"),
    matched = cms.InputTag("ca8PFJetsCHSFiltered"),
    distMax = cms.double(0.8),
    value = cms.string('mass')
)

process.ca8PFJetsCHSTrimmedMass = ca8PFJetsCHSPrunedLinks.clone(
    src = cms.InputTag("ca8PFJetsCHS"),
    matched = cms.InputTag("ca8PFJetsCHSTrimmed"),
    distMax = cms.double(0.8),
    value = cms.string('mass')
)

process.patJets.userData.userFloats.src += ['ca8PFJetsCHSPrunedMass','ca8PFJetsCHSFilteredMass','ca8PFJetsCHSTrimmedMass']

#-------------------------------------
## Enable clustering-based jet-SV association for IVF vertices and AK5 jets
#process.inclusiveSecondaryVertexFinderTagInfosAODPFlow = process.inclusiveSecondaryVertexFinderTagInfosAODPFlow.clone(
    #useSVClustering = cms.bool(True),
    ##useSVMomentum   = cms.bool(True), # otherwise using SV flight direction
    #jetAlgorithm    = cms.string("AntiKt"),
    #rParam          = cms.double(0.5),
    #ghostRescaling  = cms.double(1e-18)
#)
## Enable clustering-based jet-SV association for IVF vertices and pruned subjets of CA8 jets
process.inclusiveSecondaryVertexFinderTagInfosCA8PrunedSubjetsPFCHS = process.inclusiveSecondaryVertexFinderTagInfosCA8PrunedSubjetsPFCHS.clone(
    useSVClustering = cms.bool(True),
    #useSVMomentum   = cms.bool(True), # otherwise using SV flight direction
    jetAlgorithm    = cms.string("CambridgeAachen"),
    rParam          = cms.double(0.8),
    ghostRescaling  = cms.double(1e-18),
    fatJets         = cms.InputTag("ca8PFJetsCHS"),
    groomedFatJets   = cms.InputTag("ca8PFJetsCHSPruned")
)

#-------------------------------------
## New jet flavor still requires some cfg-level adjustments for subjets until it is better integrated into PAT
## Adjust the jet flavor for CA8 filtered subjets
process.patJetFlavourAssociationCA8FilteredSubjetsPFCHS = process.patJetFlavourAssociation.clone(
    groomedJets = cms.InputTag("ca8PFJetsCHSFiltered"),
    subjets = cms.InputTag("ca8PFJetsCHSFiltered", "SubJets")
)
process.patJetsCA8FilteredSubjetsPFCHS.JetFlavourInfoSource = cms.InputTag("patJetFlavourAssociationCA8FilteredSubjetsPFCHS","SubJets")
## Adjust the jet flavor for CA8 MassDrop-BDRS filtered subjets
process.patJetFlavourAssociationCA8MDBDRSFilteredSubjetsPFCHS = process.patJetFlavourAssociation.clone(
    groomedJets = cms.InputTag("ca8PFJetsCHSMDBDRSFiltered"),
    subjets = cms.InputTag("ca8PFJetsCHSMDBDRSFiltered", "SubJets")
)
process.patJetsCA8MDBDRSFilteredSubjetsPFCHS.JetFlavourInfoSource = cms.InputTag("patJetFlavourAssociationCA8MDBDRSFilteredSubjetsPFCHS","SubJets")
## Adjust the jet flavor for CA8 Kt-BDRS filtered subjets
process.patJetFlavourAssociationCA8KtBDRSFilteredSubjetsPFCHS = process.patJetFlavourAssociation.clone(
    groomedJets = cms.InputTag("ca8PFJetsCHSKtBDRSFiltered"),
    subjets = cms.InputTag("ca8PFJetsCHSKtBDRSFiltered", "SubJets")
)
process.patJetsCA8KtBDRSFilteredSubjetsPFCHS.JetFlavourInfoSource = cms.InputTag("patJetFlavourAssociationCA8KtBDRSFilteredSubjetsPFCHS","SubJets")
## Adjust the jet flavor for CA8 pruned subjets
process.patJetFlavourAssociationCA8PrunedSubjetsPFCHS = process.patJetFlavourAssociation.clone(
    groomedJets = cms.InputTag("ca8PFJetsCHSPruned"),
    subjets = cms.InputTag("ca8PFJetsCHSPruned", "SubJets")
)
process.patJetsCA8PrunedSubjetsPFCHS.JetFlavourInfoSource = cms.InputTag("patJetFlavourAssociationCA8PrunedSubjetsPFCHS","SubJets")
## Adjust the jet flavor for CA8 Kt subjets
process.patJetFlavourAssociationCA8KtSubjetsPFCHS = process.patJetFlavourAssociation.clone(
    groomedJets = cms.InputTag("ca8PFJetsCHSKtPruned"),
    subjets = cms.InputTag("ca8PFJetsCHSKtPruned", "SubJets")
)
process.patJetsCA8KtSubjetsPFCHS.JetFlavourInfoSource = cms.InputTag("patJetFlavourAssociationCA8KtSubjetsPFCHS","SubJets")

#-------------------------------------
## Establish references between PATified fat jets and subjets using the BoostedJetMerger
process.selectedPatJetsCA8FilteredPFCHSPacked = cms.EDProducer("BoostedJetMerger",
    jetSrc=cms.InputTag("selectedPatJetsCA8FilteredPFCHS"),
    subjetSrc=cms.InputTag("selectedPatJetsCA8FilteredSubjetsPFCHS")
)

process.selectedPatJetsCA8MDBDRSFilteredPFCHSPacked = cms.EDProducer("BoostedJetMerger",
    jetSrc=cms.InputTag("selectedPatJetsCA8MDBDRSFilteredPFCHS"),
    subjetSrc=cms.InputTag("selectedPatJetsCA8MDBDRSFilteredSubjetsPFCHS")
)

process.selectedPatJetsCA8KtBDRSFilteredPFCHSPacked = cms.EDProducer("BoostedJetMerger",
    jetSrc=cms.InputTag("selectedPatJetsCA8KtBDRSFilteredPFCHS"),
    subjetSrc=cms.InputTag("selectedPatJetsCA8KtBDRSFilteredSubjetsPFCHS")
)

process.selectedPatJetsCA8PrunedPFCHSPacked = cms.EDProducer("BoostedJetMerger",
    jetSrc=cms.InputTag("selectedPatJetsCA8PrunedPFCHS"),
    subjetSrc=cms.InputTag("selectedPatJetsCA8PrunedSubjetsPFCHS")
)

process.selectedPatJetsCA8KtPrunedPFCHSPacked = cms.EDProducer("BoostedJetMerger",
    jetSrc=cms.InputTag("selectedPatJetsCA8KtPrunedPFCHS"),
    subjetSrc=cms.InputTag("selectedPatJetsCA8KtSubjetsPFCHS")
)

## Define BoostedJetMerger sequence
process.jetMergerSeq = cms.Sequence(
    process.selectedPatJetsCA8FilteredPFCHSPacked
    + process.selectedPatJetsCA8MDBDRSFilteredPFCHSPacked
    + process.selectedPatJetsCA8KtBDRSFilteredPFCHSPacked
    + process.selectedPatJetsCA8PrunedPFCHSPacked
    + process.selectedPatJetsCA8KtPrunedPFCHSPacked
)

#-------------------------------------
from PhysicsTools.PatAlgos.tools.coreTools import *
## Remove taus from the PAT sequence
removeSpecificPATObjects(process,names=['Taus'],postfix=postfix)
## Keep only jets in the default sequence
removeAllPATObjectsBut(process, ['Jets'])

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
    for m in getattr(process,"patDefaultSequence"+postfix).moduleNames():
        if m.startswith('jetTracksAssociatorAtVertex'):
            print 'Switching ' + m + ' to explicit jet-track association'
            setattr( process, m, ak5JetTracksAssociatorExplicit.clone(jets = getattr(getattr(process,m),'jets')) )
    for m in getattr(process,"patDefaultSequence").moduleNames():
        if m.startswith('jetTracksAssociatorAtVertex'):
            print 'Switching ' + m + ' to explicit jet-track association'
            setattr( process, m, ak5JetTracksAssociatorExplicit.clone(jets = getattr(getattr(process,m),'jets')) )

#-------------------------------------
## Remove tau stuff that really shouldn't be there (probably a bug in PAT)
process.patDefaultSequence.remove(process.kt6PFJetsForRhoComputationVoronoi)
for m in getattr(process,"patDefaultSequence").moduleNames():
    if m.startswith('hpsPFTau'):
        getattr(process,"patDefaultSequence").remove(getattr(process,m))

process.patDefaultSequencePFlow.remove(process.kt6PFJetsForRhoComputationVoronoiPFlow)
for m in getattr(process,"patDefaultSequence"+postfix).moduleNames():
    if m.startswith('hpsPFTau'):
        getattr(process,"patDefaultSequence"+postfix).remove(getattr(process,m))
#-------------------------------------
## Define jet sequences
process.genJetSeq = cms.Sequence(
    process.ca8GenJetsNoNu
    + process.ca8GenJetsNoNuFiltered
    + process.ca8GenJetsNoNuMDBDRSFiltered
    + process.ca8GenJetsNoNuKtBDRSFiltered
    + process.ca8GenJetsNoNuPruned
    + process.ca8GenJetsNoNuKtPruned
)
process.jetSeq = cms.Sequence(
    (
    process.ca8PFJetsCHS
    + process.ca8PFJetsCHSFiltered
    + process.ca8PFJetsCHSMDBDRSFiltered
    + process.ca8PFJetsCHSKtBDRSFiltered
    + process.ca8PFJetsCHSPruned
    + process.ca8PFJetsCHSKtPruned
    + process.ca8PFJetsCHSTrimmed
    )
    * (
    process.NjettinessCA8
    + process.ca8PFJetsCHSFilteredMass
    + process.ca8PFJetsCHSPrunedMass
    + process.ca8PFJetsCHSTrimmedMass
    )
)

if not options.runOnData:
    process.jetSeq = cms.Sequence( process.genJetSeq + process.jetSeq )

#-------------------------------------
## Adapt primary vertex collection
from PhysicsTools.PatAlgos.tools.pfTools import *
adaptPVs(process, pvCollection=cms.InputTag('goodOfflinePrimaryVertices'), postfix=postfix, sequence='patPF2PATSequence')
adaptPVs(process, pvCollection=cms.InputTag('goodOfflinePrimaryVertices'), postfix='', sequence='jetSeq')
adaptPVs(process, pvCollection=cms.InputTag('goodOfflinePrimaryVertices'), postfix='', sequence='patDefaultSequence')

#-------------------------------------
## Path definition
process.p = cms.Path(
    process.primaryVertexFilter
    * process.goodOfflinePrimaryVertices
    * (
    getattr(process,"patPF2PATSequence"+postfix)
    + ( process.jetSeq * process.patDefaultSequence )
    )
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
