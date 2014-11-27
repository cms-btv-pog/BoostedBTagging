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
options.register('jetAlgo', 'CambridgeAachen',
    VarParsing.multiplicity.singleton,
    VarParsing.varType.string,
    "Jet clustering algorithms (default is CambridgeAachen)"
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
inputJetCorrLabelAK5 = ('AK5PFchs', ['L1FastJet', 'L2Relative', 'L3Absolute'])
inputJetCorrLabelAK7 = ('AK7PFchs', ['L1FastJet', 'L2Relative', 'L3Absolute'])

if not options.usePFchs:
    inputJetCorrLabelAK5 = ('AK5PF', ['L1FastJet', 'L2Relative', 'L3Absolute'])
    inputJetCorrLabelAK7 = ('AK7PF', ['L1FastJet', 'L2Relative', 'L3Absolute'])

if options.runOnData:
    inputJetCorrLabelAK5[1].append('L2L3Residual')
    inputJetCorrLabelAK7[1].append('L2L3Residual')

## b tagging
bTagInfos = ['impactParameterTagInfos','secondaryVertexTagInfos','inclusiveSecondaryVertexFinderTagInfos'
             ,'softMuonTagInfos','secondaryVertexNegativeTagInfos']
             #,'inclusiveSecondaryVertexFinderFilteredTagInfos']
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

process = cms.Process("USER")

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
process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(options.wantSummary) )

#-------------------------------------
## Input files
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        'file:patTuple_PF2PAT_mc.root'
    )
)

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

#-------------------------------------
## Fat jets (Gen and Reco)
from RecoJets.JetProducers.ca4GenJets_cfi import ca4GenJets
process.genJetsNoNu = ca4GenJets.clone(
    jetAlgorithm = cms.string(options.jetAlgo),
    rParam = cms.double(options.jetRadius),
    src = cms.InputTag("genParticlesForJetsNoNu")
)
from RecoJets.JetProducers.ca4PFJets_cfi import ca4PFJets
process.PFJetsCHS = ca4PFJets.clone(
    jetAlgorithm = cms.string(options.jetAlgo),
    rParam = cms.double(options.jetRadius),
    src = cms.InputTag("pfNoElectronPFlow"),
    srcPVs = cms.InputTag("goodOfflinePrimaryVertices"),
    doAreaFastjet = cms.bool(True),
    jetPtMin = cms.double(20.)
)
## Filtered fat jets (Gen and Reco) (each module produces two jet collections, fat jets and subjets)
from RecoJets.JetProducers.ca4GenJets_cfi import ca4GenJets
process.genJetsNoNuFiltered = ca4GenJets.clone(
    jetAlgorithm = cms.string(options.jetAlgo),
    rParam = cms.double(options.jetRadius),
    src = cms.InputTag("genParticlesForJetsNoNu"),
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
    src = process.PFJetsCHS.src,
    srcPVs = process.PFJetsCHS.srcPVs,
    doAreaFastjet = process.PFJetsCHS.doAreaFastjet,
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
process.PFJetsCHSMDBDRSFiltered = ak5PFJetsMassDropFiltered.clone(
    jetAlgorithm = cms.string(options.jetAlgo),
    rParam = cms.double(options.jetRadius),
    src = process.PFJetsCHS.src,
    srcPVs = process.PFJetsCHS.srcPVs,
    doAreaFastjet = process.PFJetsCHS.doAreaFastjet,
    writeCompound = cms.bool(True),
    jetCollInstanceName=cms.string("SubJets"),
    jetPtMin = cms.double(20.),
    useDynamicFiltering = cms.bool(True),
    rFiltFactor = cms.double(0.5)
)
## Kt-BDRS filtered fat jets (Gen and Reco) (each module produces two jet collections, fat jets and subjets)
## Compared to the above filtered jets, here dynamic filtering radius is used (as in arXiv:0802.2470)
## However, here the mass drop is replaced by finding two Kt subjets which then set the size of the filtering radius
from RecoJets.JetProducers.ca4GenJets_cfi import ca4GenJets
process.genJetsNoNuKtBDRSFiltered = ca4GenJets.clone(
    jetAlgorithm = cms.string(options.jetAlgo),
    rParam = cms.double(options.jetRadius),
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
process.PFJetsCHSKtBDRSFiltered = ak5PFJetsFiltered.clone(
    jetAlgorithm = cms.string(options.jetAlgo),
    rParam = cms.double(options.jetRadius),
    src = process.PFJetsCHS.src,
    srcPVs = process.PFJetsCHS.srcPVs,
    doAreaFastjet = process.PFJetsCHS.doAreaFastjet,
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
## Pruned fat jets (Gen and Reco) (each module produces two jet collections, fat jets and subjets)
from RecoJets.JetProducers.SubJetParameters_cfi import SubJetParameters
process.genJetsNoNuPruned = ca4GenJets.clone(
    SubJetParameters,
    jetAlgorithm = cms.string(options.jetAlgo),
    rParam = cms.double(options.jetRadius),
    src = cms.InputTag("genParticlesForJetsNoNu"),
    usePruning = cms.bool(True),
    writeCompound = cms.bool(True),
    jetCollInstanceName=cms.string("SubJets")
)
from RecoJets.JetProducers.ak5PFJetsPruned_cfi import ak5PFJetsPruned
process.PFJetsCHSPruned = ak5PFJetsPruned.clone(
    jetAlgorithm = cms.string(options.jetAlgo),
    rParam = cms.double(options.jetRadius),
    src = process.PFJetsCHS.src,
    srcPVs = process.PFJetsCHS.srcPVs,
    doAreaFastjet = process.PFJetsCHS.doAreaFastjet,
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
    src = cms.InputTag("genParticlesForJetsNoNu"),
    usePruning = cms.bool(True),
    useKtPruning = cms.bool(True),
    writeCompound = cms.bool(True),
    jetCollInstanceName=cms.string("SubJets")
)
from RecoJets.JetProducers.ak5PFJetsPruned_cfi import ak5PFJetsPruned
process.PFJetsCHSKtPruned = ak5PFJetsPruned.clone(
    jetAlgorithm = cms.string(options.jetAlgo),
    rParam = cms.double(options.jetRadius),
    src = process.PFJetsCHS.src,
    srcPVs = process.PFJetsCHS.srcPVs,
    doAreaFastjet = process.PFJetsCHS.doAreaFastjet,
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
    src = process.PFJetsCHS.src,
    srcPVs = process.PFJetsCHS.srcPVs,
    doAreaFastjet = process.PFJetsCHS.doAreaFastjet,
    jetPtMin = cms.double(20.)
)

#-------------------------------------
## PATify the above jets
from PhysicsTools.PatAlgos.tools.jetTools import *
## Fat jets
switchJetCollection(process,
    jetCollection=cms.InputTag('PFJetsCHS'),
    jetIdLabel=algoLabel,
    rParam=options.jetRadius,
    useLegacyFlavour=False,
    doJTA=options.doJTA,
    doBTagging=options.doBTagging,
    btagInfo=bTagInfos,
    btagdiscriminators=bTagDiscriminators,
    jetCorrLabel = inputJetCorrLabelAK5,
    doType1MET   = False,
    genJetCollection = cms.InputTag("genJetsNoNu"),
    doJetID      = False,
)
## Filtered fat jets
addJetCollection(process,
    jetCollection=cms.InputTag('PFJetsCHSFiltered'),
    algoLabel=algoLabel,
    typeLabel='FilteredPFCHS',
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
    genJetCollection=cms.InputTag("genJetsNoNu")
)
## Filtered subjets of fat jets
addJetCollection(process,
    jetCollection=cms.InputTag('PFJetsCHSFiltered','SubJets'),
    algoLabel=algoLabel,
    typeLabel='FilteredSubjetsPFCHS',
    rParam=options.jetRadius,
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
    genJetCollection=cms.InputTag('genJetsNoNuFiltered','SubJets')
)
## MassDrop-BDRS filtered fat jets
#addJetCollection(process,
    #jetCollection=cms.InputTag('PFJetsCHSMDBDRSFiltered'),
    #algoLabel=algoLabel,
    #typeLabel='MDBDRSFilteredPFCHS',
    #getJetMCFlavour=False,
    #doJTA=False,
    #doBTagging=False,
    #btagInfo=bTagInfos,
    #btagdiscriminators=bTagDiscriminators,
    #jetCorrLabel=inputJetCorrLabelAK7,
    #doType1MET=False,
    #doL1Cleaning=False,
    #doL1Counters=False,
    #doJetID=False,
    #genJetCollection=cms.InputTag("genJetsNoNu")
#)
## MassDrop-BDRS filtered subjets of fat jets
#addJetCollection(process,
    #jetCollection=cms.InputTag('PFJetsCHSMDBDRSFiltered','SubJets'),
    #algoLabel=algoLabel,
    #typeLabel='MDBDRSFilteredSubjetsPFCHS',
    #rParam=options.jetRadius,
    #useLegacyFlavour=False,
    #doJTA=options.doJTA,
    #doBTagging=options.doBTagging,
    #btagInfo=bTagInfos,
    #btagdiscriminators=bTagDiscriminators,
    #jetCorrLabel=inputJetCorrLabelAK5,
    #doType1MET=False,
    #doL1Cleaning=False,
    #doL1Counters=False,
    #doJetID=False,
    #genJetCollection=cms.InputTag('genJetsNoNuMDBDRSFiltered','SubJets')
#)
## Kt-BDRS filtered fat jets
addJetCollection(process,
    jetCollection=cms.InputTag('PFJetsCHSKtBDRSFiltered'),
    algoLabel=algoLabel,
    typeLabel='KtBDRSFilteredPFCHS',
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
    genJetCollection=cms.InputTag("genJetsNoNu")
)
## Kt-BDRS filtered subjets of fat jets
addJetCollection(process,
    jetCollection=cms.InputTag('PFJetsCHSKtBDRSFiltered','SubJets'),
    algoLabel=algoLabel,
    typeLabel='KtBDRSFilteredSubjetsPFCHS',
    rParam=options.jetRadius,
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
    genJetCollection=cms.InputTag('genJetsNoNuKtBDRSFiltered','SubJets')
)
## Pruned fat jets
addJetCollection(process,
    jetCollection=cms.InputTag('PFJetsCHSPruned'),
    algoLabel=algoLabel,
    typeLabel='PrunedPFCHS',
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
    genJetCollection=cms.InputTag("genJetsNoNu")
)
## Pruned subjets of fat jets
addJetCollection(process,
    jetCollection=cms.InputTag('PFJetsCHSPruned','SubJets'),
    algoLabel=algoLabel,
    typeLabel='PrunedSubjetsPFCHS',
    rParam=options.jetRadius,
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
    genJetCollection=cms.InputTag('genJetsNoNuPruned','SubJets')
)
## Kt pruned fat jets
addJetCollection(process,
    jetCollection=cms.InputTag('PFJetsCHSKtPruned'),
    algoLabel=algoLabel,
    typeLabel='KtPrunedPFCHS',
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
    genJetCollection=cms.InputTag("genJetsNoNu")
)
## Kt subjets of fat jets
addJetCollection(process,
    jetCollection=cms.InputTag('PFJetsCHSKtPruned','SubJets'),
    algoLabel=algoLabel,
    typeLabel='KtSubjetsPFCHS',
    rParam=options.jetRadius,
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
    genJetCollection=cms.InputTag('genJetsNoNuKtPruned','SubJets')
)

#-------------------------------------
## N-subjettiness
from RecoJets.JetProducers.nJettinessAdder_cfi import Njettiness

process.Njettiness = Njettiness.clone(
    src = cms.InputTag("PFJetsCHS"),
    cone = cms.double(options.jetRadius)
)

process.patJets.userData.userFloats.src += ['Njettiness:tau1','Njettiness:tau2','Njettiness:tau3']

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

process.patJets.userData.userFloats.src += ['PFJetsCHSPrunedMass','PFJetsCHSFilteredMass','PFJetsCHSTrimmedMass','PFJetsCHSPrunedPt','PFJetsCHSFilteredPt','PFJetsCHSTrimmedPt']

#-------------------------------------
if options.useSVClustering:
    ## Enable clustering-based jet-SV association for IVF vertices and AK5 jets (not really needed here since it is mostly intended for subjets)
    #process.inclusiveSecondaryVertexFinderTagInfosAODPFlow = process.inclusiveSecondaryVertexFinderTagInfosAODPFlow.clone(
        #useSVClustering = cms.bool(True),
        ##useSVMomentum   = cms.bool(True), # otherwise using SV flight direction
        #jetAlgorithm    = cms.string("AntiKt"),
        #rParam          = cms.double(0.5),
        #ghostRescaling  = cms.double(1e-18)
    #)
    ## Enable clustering-based jet-SV association for IVF vertices and subjets of fat jets
    setattr(process,'inclusiveSecondaryVertexFinderTagInfos'+algoLabel+'FilteredSubjetsPFCHS', getattr(process,'inclusiveSecondaryVertexFinderTagInfos'+algoLabel+'FilteredSubjetsPFCHS').clone(
        useSVClustering = cms.bool(True),
        useSVMomentum   = cms.bool(options.useSVMomentum), # otherwise using SV flight direction
        jetAlgorithm    = cms.string(options.jetAlgo),
        rParam          = cms.double(options.jetRadius),
        ghostRescaling  = cms.double(1e-18),
        fatJets         = cms.InputTag("PFJetsCHS"),
        groomedFatJets  = cms.InputTag("PFJetsCHSFiltered")
    ))
    #setattr(process,'inclusiveSecondaryVertexFinderTagInfos'+algoLabel+'MDBDRSFilteredSubjetsPFCHS', getattr(process,'inclusiveSecondaryVertexFinderTagInfos'+algoLabel+'MDBDRSFilteredSubjetsPFCHS').clone(
        #useSVClustering = cms.bool(True),
        #useSVMomentum   = cms.bool(options.useSVMomentum), # otherwise using SV flight direction
        #jetAlgorithm    = cms.string(options.jetAlgo),
        #rParam          = cms.double(options.jetRadius),
        #ghostRescaling  = cms.double(1e-18),
        #fatJets         = cms.InputTag("PFJetsCHS"),
        #groomedFatJets  = cms.InputTag("PFJetsCHSMDBDRSFiltered")
    #))
    setattr(process,'inclusiveSecondaryVertexFinderTagInfos'+algoLabel+'KtBDRSFilteredSubjetsPFCHS', getattr(process,'inclusiveSecondaryVertexFinderTagInfos'+algoLabel+'KtBDRSFilteredSubjetsPFCHS').clone(
        useSVClustering = cms.bool(True),
        useSVMomentum   = cms.bool(options.useSVMomentum), # otherwise using SV flight direction
        jetAlgorithm    = cms.string(options.jetAlgo),
        rParam          = cms.double(options.jetRadius),
        ghostRescaling  = cms.double(1e-18),
        fatJets         = cms.InputTag("PFJetsCHS"),
        groomedFatJets  = cms.InputTag("PFJetsCHSKtBDRSFiltered")
    ))
    setattr(process,'inclusiveSecondaryVertexFinderTagInfos'+algoLabel+'PrunedSubjetsPFCHS', getattr(process,'inclusiveSecondaryVertexFinderTagInfos'+algoLabel+'PrunedSubjetsPFCHS').clone(
        useSVClustering = cms.bool(True),
        useSVMomentum   = cms.bool(options.useSVMomentum), # otherwise using SV flight direction
        jetAlgorithm    = cms.string(options.jetAlgo),
        rParam          = cms.double(options.jetRadius),
        ghostRescaling  = cms.double(1e-18),
        fatJets         = cms.InputTag("PFJetsCHS"),
        groomedFatJets  = cms.InputTag("PFJetsCHSPruned")
    ))
    setattr(process,'inclusiveSecondaryVertexFinderTagInfos'+algoLabel+'KtSubjetsPFCHS', getattr(process,'inclusiveSecondaryVertexFinderTagInfos'+algoLabel+'KtSubjetsPFCHS').clone(
        useSVClustering = cms.bool(True),
        useSVMomentum   = cms.bool(options.useSVMomentum), # otherwise using SV flight direction
        jetAlgorithm    = cms.string(options.jetAlgo),
        rParam          = cms.double(options.jetRadius),
        ghostRescaling  = cms.double(1e-18),
        fatJets         = cms.InputTag("PFJetsCHS"),
        groomedFatJets  = cms.InputTag("PFJetsCHSKtPruned")
    ))

#-------------------------------------
## New jet flavor still requires some cfg-level adjustments for subjets until it is better integrated into PAT
## Adjust the jet flavor for filtered subjets
setattr(process,'patJetFlavourAssociation'+algoLabel+'FilteredSubjetsPFCHS', process.patJetFlavourAssociation.clone(
    groomedJets = cms.InputTag("PFJetsCHSFiltered"),
    subjets = cms.InputTag("PFJetsCHSFiltered", "SubJets")
))
getattr(process,'patJets'+algoLabel+'FilteredSubjetsPFCHS').JetFlavourInfoSource = cms.InputTag("patJetFlavourAssociation"+algoLabel+"FilteredSubjetsPFCHS","SubJets")
## Adjust the jet flavor for MassDrop-BDRS filtered subjets
#setattr(process,'patJetFlavourAssociation'+algoLabel+'MDBDRSFilteredSubjetsPFCHS', process.patJetFlavourAssociation.clone(
    #groomedJets = cms.InputTag("PFJetsCHSMDBDRSFiltered"),
    #subjets = cms.InputTag("PFJetsCHSMDBDRSFiltered", "SubJets")
#))
#getattr(process,'patJets'+algoLabel+'MDBDRSFilteredSubjetsPFCHS').JetFlavourInfoSource = cms.InputTag("patJetFlavourAssociation"+algoLabel+"MDBDRSFilteredSubjetsPFCHS","SubJets")
## Adjust the jet flavor for Kt-BDRS filtered subjets
setattr(process,'patJetFlavourAssociation'+algoLabel+'KtBDRSFilteredSubjetsPFCHS', process.patJetFlavourAssociation.clone(
    groomedJets = cms.InputTag("PFJetsCHSKtBDRSFiltered"),
    subjets = cms.InputTag("PFJetsCHSKtBDRSFiltered", "SubJets")
))
getattr(process,'patJets'+algoLabel+'KtBDRSFilteredSubjetsPFCHS').JetFlavourInfoSource = cms.InputTag("patJetFlavourAssociation"+algoLabel+"KtBDRSFilteredSubjetsPFCHS","SubJets")
## Adjust the jet flavor for pruned subjets
setattr(process,'patJetFlavourAssociation'+algoLabel+'PrunedSubjetsPFCHS', process.patJetFlavourAssociation.clone(
    groomedJets = cms.InputTag("PFJetsCHSPruned"),
    subjets = cms.InputTag("PFJetsCHSPruned", "SubJets")
))
getattr(process,'patJets'+algoLabel+'PrunedSubjetsPFCHS').JetFlavourInfoSource = cms.InputTag("patJetFlavourAssociation"+algoLabel+"PrunedSubjetsPFCHS","SubJets")
## Adjust the jet flavor for Kt subjets
setattr(process,'patJetFlavourAssociation'+algoLabel+'KtSubjetsPFCHS', process.patJetFlavourAssociation.clone(
    groomedJets = cms.InputTag("PFJetsCHSKtPruned"),
    subjets = cms.InputTag("PFJetsCHSKtPruned", "SubJets")
))
getattr(process,'patJets'+algoLabel+'KtSubjetsPFCHS').JetFlavourInfoSource = cms.InputTag("patJetFlavourAssociation"+algoLabel+"KtSubjetsPFCHS","SubJets")

#-------------------------------------
## Establish references between PATified fat jets and subjets using the BoostedJetMerger
process.selectedPatJetsFilteredPFCHSPacked = cms.EDProducer("BoostedJetMerger",
    jetSrc=cms.InputTag("selectedPatJets"+algoLabel+"FilteredPFCHS"),
    subjetSrc=cms.InputTag("selectedPatJets"+algoLabel+"FilteredSubjetsPFCHS")
)

#process.selectedPatJetsMDBDRSFilteredPFCHSPacked = cms.EDProducer("BoostedJetMerger",
    #jetSrc=cms.InputTag("selectedPatJets"+algoLabel+"MDBDRSFilteredPFCHS"),
    #subjetSrc=cms.InputTag("selectedPatJets"+algoLabel+"MDBDRSFilteredSubjetsPFCHS")
#)

process.selectedPatJetsKtBDRSFilteredPFCHSPacked = cms.EDProducer("BoostedJetMerger",
    jetSrc=cms.InputTag("selectedPatJets"+algoLabel+"KtBDRSFilteredPFCHS"),
    subjetSrc=cms.InputTag("selectedPatJets"+algoLabel+"KtBDRSFilteredSubjetsPFCHS")
)

process.selectedPatJetsPrunedPFCHSPacked = cms.EDProducer("BoostedJetMerger",
    jetSrc=cms.InputTag("selectedPatJets"+algoLabel+"PrunedPFCHS"),
    subjetSrc=cms.InputTag("selectedPatJets"+algoLabel+"PrunedSubjetsPFCHS")
)

process.selectedPatJetsKtPrunedPFCHSPacked = cms.EDProducer("BoostedJetMerger",
    jetSrc=cms.InputTag("selectedPatJets"+algoLabel+"KtPrunedPFCHS"),
    subjetSrc=cms.InputTag("selectedPatJets"+algoLabel+"KtSubjetsPFCHS")
)

## Define BoostedJetMerger sequence
process.jetMergerSeq = cms.Sequence(
    process.selectedPatJetsFilteredPFCHSPacked
    #+ process.selectedPatJetsMDBDRSFilteredPFCHSPacked
    + process.selectedPatJetsKtBDRSFilteredPFCHSPacked
    + process.selectedPatJetsPrunedPFCHSPacked
    + process.selectedPatJetsKtPrunedPFCHSPacked
)

#-------------------------------------
from PhysicsTools.PatAlgos.tools.coreTools import *
## Keep only jets in the default sequence
removeAllPATObjectsBut(process, ['Jets','Muons'])

## Remove MC matching when running over data
if options.runOnData:
    removeMCMatching( process, ['All'] )

#-------------------------------------
## GenParticles for GenJets
from RecoJets.Configuration.GenJetParticles_cff import genParticlesForJetsNoNu
process.genParticlesForJetsNoNu = genParticlesForJetsNoNu

#-------------------------------------
## Add GenParticlePruner for boosted b-tagging studies
process.prunedGenParticlesBoost = cms.EDProducer('GenParticlePruner',
    src = cms.InputTag("genParticles"),
    select = cms.vstring(
        "drop  *  ", #by default
        "keep ( status = 3 || (status>=21 && status<=29) )", #keep hard process particles
        "keep abs(pdgId) = 13 || abs(pdgId) = 15" #keep muons and taus
    )
)

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
process.load("RecoBTag.PerformanceMeasurements.BTagAnalyzer_cff")
# The following combinations should be considered:
# For b-tagging performance measurements:
#   process.btagana.useSelectedTracks    = True
#   process.btagana.useTrackHistory      = False (or True for Mistag systematics with GEN-SIM-RECODEBUG samples)
#   process.btagana.produceJetTrackTree  = False
#   process.btagana.produceAllTrackTree  = False
#   process.btagana.producePtRelTemplate = False (or True for PtRel fit studies)
# or data/MC validation of jets, tracks and SVs:
#   process.btagana.useSelectedTracks    = False (or True for JP calibration)
#   process.btagana.useTrackHistory      = False
#   process.btagana.produceJetTrackTree  = True
#   process.btagana.produceAllTrackTree  = False
#   process.btagana.producePtRelTemplate = False
# or general tracks, PV and jet performance studies:
#   process.btagana.useSelectedTracks    = True
#   process.btagana.useTrackHistory      = False
#   process.btagana.produceJetTrackTree  = False
#   process.btagana.produceAllTrackTree  = True
#   process.btagana.producePtRelTemplate = False
#------------------
process.btagana.useSelectedTracks     = True  ## False if you want to run on all tracks : for commissioning studies
process.btagana.useTrackHistory       = False ## Can only be used with GEN-SIM-RECODEBUG files
process.btagana.produceJetTrackTree   = False ## True if you want to keep info for tracks associated to jets : for commissioning studies
process.btagana.produceAllTrackTree   = False ## True if you want to keep info for all tracks : for commissioning studies
process.btagana.producePtRelTemplate  = False  ## True for performance studies
#------------------
process.btagana.storeTagVariables     = True ## True if you want to keep TagInfo TaggingVariables
process.btagana.storeCSVTagVariables  = True ## True if you want to keep CSV TaggingVariables
process.btagana.primaryVertexColl     = cms.InputTag('goodOfflinePrimaryVertices')
process.btagana.Jets                  = cms.InputTag('selectedPatJets')
process.btagana.patMuonCollectionName = cms.InputTag('selectedPatMuons')
process.btagana.use_ttbar_filter      = cms.bool(False)
process.btagana.triggerTable          = cms.InputTag('TriggerResults::HLT') # Data and MC
process.btagana.svComputer            = cms.string('combinedSecondaryVertexV2')

process.btaganaSubJets = process.btagana.clone(
    storeEventInfo       = cms.bool(True),
    storeTagVariables    = cms.bool(True),
    storeCSVTagVariables = cms.bool(True),
    allowJetSkipping     = cms.bool(False),
    Jets                 = cms.InputTag('selectedPatJets'+algoLabel+'PrunedSubjetsPFCHS'),
    FatJets              = cms.InputTag('selectedPatJets'),
    GroomedFatJets       = cms.InputTag('selectedPatJetsPrunedPFCHSPacked'),
    runSubJets           = cms.bool(True),
    svComputer           = cms.string('combinedSecondaryVertexV2'),
    svComputerFatJets    = cms.string('combinedSecondaryVertexV2Fat')
)

#-------------------------------------
## If using explicit jet-track association
if options.useExplicitJTA:
    from RecoJets.JetAssociationProducers.ak5JTA_cff import ak5JetTracksAssociatorExplicit
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

#-------------------------------------
## Define jet sequences
process.genJetSeq = cms.Sequence(
    process.genJetsNoNu
    + process.genJetsNoNuFiltered
    #+ process.genJetsNoNuMDBDRSFiltered
    + process.genJetsNoNuKtBDRSFiltered
    + process.genJetsNoNuPruned
    + process.genJetsNoNuKtPruned
)
process.jetSeq = cms.Sequence(
    (
    process.PFJetsCHS
    + process.PFJetsCHSFiltered
    #+ process.PFJetsCHSMDBDRSFiltered
    + process.PFJetsCHSKtBDRSFiltered
    + process.PFJetsCHSPruned
    + process.PFJetsCHSKtPruned
    + process.PFJetsCHSTrimmed
    )
    * (
    process.Njettiness
    + process.PFJetsCHSFilteredMass
    + process.PFJetsCHSPrunedMass
    + process.PFJetsCHSTrimmedMass
    + process.PFJetsCHSFilteredPt
    + process.PFJetsCHSPrunedPt
    + process.PFJetsCHSTrimmedPt
    )
)

if not options.runOnData:
    process.jetSeq = cms.Sequence( process.genParticlesForJetsNoNu * process.genJetSeq + process.jetSeq )

#-------------------------------------
## Adapt primary vertex collection
from PhysicsTools.PatAlgos.tools.pfTools import *
adaptPVs(process, pvCollection=cms.InputTag('goodOfflinePrimaryVertices'), postfix='', sequence='jetSeq')
adaptPVs(process, pvCollection=cms.InputTag('goodOfflinePrimaryVertices'), postfix='', sequence='patDefaultSequence')

#-------------------------------------
## Add full JetFlavourInfo and TagInfos to PAT jets
for m in ['patJets', 'patJets'+algoLabel+'FilteredSubjetsPFCHS', 'patJets'+algoLabel+'MDBDRSFilteredSubjetsPFCHS', 'patJets'+algoLabel+'KtBDRSFilteredSubjetsPFCHS',
          'patJets'+algoLabel+'PrunedSubjetsPFCHS', 'patJets'+algoLabel+'KtSubjetsPFCHS']:
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
    process.jetTracksAssociatorAtVertex.coneSize = cms.double(options.jetRadius) # default is 0.5
    process.secondaryVertexTagInfosAOD.trackSelection.jetDeltaRMax = cms.double(options.jetRadius)   # default is 0.3
    process.secondaryVertexTagInfosAOD.vertexCuts.maxDeltaRToJetAxis = cms.double(options.jetRadius) # default is 0.5
    # Set the jet-SV dR to the jet radius
    process.inclusiveSecondaryVertexFinderTagInfosAOD.vertexCuts.maxDeltaRToJetAxis = cms.double(options.jetRadius) # default is 0.5
    process.inclusiveSecondaryVertexFinderTagInfosAOD.extSVDeltaRToJet = cms.double(options.jetRadius) # default is 0.3
    # Set the JP track dR cut to the jet radius
    process.jetProbabilityFat = process.jetProbability.clone( deltaR = cms.double(options.jetRadius) ) # default is 0.3
    process.jetProbabilityBJetTagsAOD.jetTagComputer = cms.string('jetProbabilityFat')
    # Set the JBP track dR cut to the jet radius
    process.jetBProbabilityFat = process.jetBProbability.clone( deltaR = cms.double(options.jetRadius) ) # default is 0.5
    process.jetBProbabilityBJetTagsAOD.jetTagComputer = cms.string('jetBProbabilityFat')
    # Set the CSV track dR cut to the jet radius
    process.combinedSecondaryVertexFat = process.combinedSecondaryVertex.clone()
    process.combinedSecondaryVertexFat.trackSelection.jetDeltaRMax = cms.double(options.jetRadius) # default is 0.3
    process.combinedSecondaryVertexFat.trackPseudoSelection.jetDeltaRMax = cms.double(options.jetRadius) # default is 0.3
    process.combinedSecondaryVertexBJetTagsAOD.jetTagComputer = cms.string('combinedSecondaryVertexFat')
    # Set the CSVV2 track dR cut to the jet radius
    process.combinedSecondaryVertexV2Fat = process.combinedSecondaryVertexV2.clone()
    process.combinedSecondaryVertexV2Fat.trackSelection.jetDeltaRMax = cms.double(options.jetRadius) # default is 0.3
    process.combinedSecondaryVertexV2Fat.trackPseudoSelection.jetDeltaRMax = cms.double(options.jetRadius) # default is 0.3
    process.combinedInclusiveSecondaryVertexV2BJetTagsAOD.jetTagComputer = cms.string('combinedSecondaryVertexV2Fat')

#-------------------------------------
## Path definition
process.p = cms.Path(
    process.prunedGenParticlesBoost
    * process.primaryVertexFilter
    * process.goodOfflinePrimaryVertices
    * ( process.jetSeq * process.patDefaultSequence )
    * process.jetMergerSeq
    * (
    process.btaganaSubJets
    )
)

## Delete output module
del process.out

## Schedule definition
process.schedule = cms.Schedule(process.p)
