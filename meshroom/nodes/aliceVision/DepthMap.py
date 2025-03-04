__version__ = "3.0"

from meshroom.core import desc


class DepthMap(desc.AVCommandLineNode):
    commandLine = 'aliceVision_depthMapEstimation {allParams}'
    gpu = desc.Level.INTENSIVE
    size = desc.DynamicNodeSize('input')
    parallelization = desc.Parallelization(blockSize=3)
    commandLineRange = '--rangeStart {rangeStart} --rangeSize {rangeBlockSize}'

    category = 'Dense Reconstruction'
    documentation = '''
Estimate a depth map for each calibrated camera using Plane Sweeping, a multi-view stereo algorithm notable for its efficiency on modern graphics hardware (GPU).

Adjust the downscale factor to compute depth maps at a higher/lower resolution.
Use a downscale factor of one (full-resolution) only if the quality of the input images is really high (camera on a tripod with high-quality optics).

## Online
[https://alicevision.org/#photogrammetry/depth_maps_estimation](https://alicevision.org/#photogrammetry/depth_maps_estimation)
'''

    inputs = [
        desc.File(
            name='input',
            label='SfMData',
            description='SfMData file.',
            value='',
            uid=[0],
        ),
        desc.File(
            name='imagesFolder',
            label='Images Folder',
            description='Use images from a specific folder instead of those specify in the SfMData file.\nFilename should be the image uid.',
            value='',
            uid=[0],
        ),
       desc.ChoiceParam(
            name='downscale',
            label='Downscale',
            description='Downscale the input images to compute the depth map.\n'
                        'Full resolution (downscale=1) gives the best result,\n'
                        'but using a larger downscale will reduce computation time at the expense of quality.\n'
                        'If the images are noisy, blurry or if the surfaces are challenging (weakly-textured or with specularities) a larger downscale may improve.',
            value=2,
            values=[1, 2, 4, 8, 16],
            exclusive=True,
            uid=[0],
        ),
        desc.FloatParam(
            name='minViewAngle',
            label='Min View Angle',
            description='Minimum angle between two views (select the neighbouring cameras, select depth planes from epipolar segment point).',
            value=2.0,
            range=(0.0, 10.0, 0.1),
            uid=[0],
            advanced=True,
        ),
        desc.FloatParam(
            name='maxViewAngle',
            label='Max View Angle',
            description='Maximum angle between two views (select the neighbouring cameras, select depth planes from epipolar segment point).',
            value=70.0,
            range=(10.0, 120.0, 1.0),
            uid=[0],
            advanced=True,
        ),
        desc.GroupAttribute(
            name='tiling',
            label='Tiling',
            description='Tiles are used to split the computation into fixed buffers to best fit the GPU.',
            group=None,
            groupDesc=[
            desc.IntParam(
                name='tileBufferWidth',
                label='Buffer Width',
                description='Maximum tile buffer width.',
                value=1024,
                range=(-1, 2000, 10),
                uid=[0],
            ),
            desc.IntParam(
                name='tileBufferHeight',
                label='Buffer Height',
                description='Maximum tile buffer height.',
                value=1024,
                range=(-1, 2000, 10),
                uid=[0],
            ),
            desc.IntParam(
                name='tilePadding',
                label='Padding',
                description='Buffer padding for overlapping tiles.',
                value=64,
                range=(0, 500, 1),
                uid=[0],
            ),
            desc.BoolParam(
                name='autoAdjustSmallImage',
                label='Auto Adjust Small Image',
                description='Automatically adjust depth map parameters if images are smaller than one tile (maxTCamsPerTile=maxTCams, adjust step if needed).',
                value=True,
                uid=[0],
                advanced=True,
            ),
        ]),
        desc.BoolParam(
            name='chooseTCamsPerTile',
            label='Choose Neighbour Cameras Per Tile',
            description='Choose neighbour cameras per tile or globally to the image.',
            value=True,
            uid=[0],
            advanced=True,
        ),
        desc.IntParam(
            name='maxTCams',
            label='Max Nb Neighbour Cameras',
            description='Maximum number of neighbour cameras per image.',
            value=10,
            range=(1, 20, 1),
            uid=[0],
        ),
        desc.GroupAttribute(
            name='sgm',
            label='SGM',
            description='Semi-Global Matching (SGM) step computes a similarity volume and extracts the initial low-resolution depth map.\n'
                        'This method is highly robust but has limited depth precision (banding artifacts due to a limited list of depth planes).',
            group=None,
            groupDesc=[
            desc.IntParam(
                name='sgmScale',
                label='Downscale Factor',
                description='Downscale factor applied on source images for the SGM step (in addition to the global downscale).',
                value=2,
                range=(-1, 10, 1),
                uid=[0],
            ),
            desc.IntParam(
                name='sgmStepXY',
                label='Step XY',
                description='The step is used to compute the similarity volume for one pixel over N (in the XY image plane).',
                value=2,
                range=(-1, 10, 1),
                uid=[0],
            ),
            desc.IntParam(
                name='sgmStepZ',
                label='Step Z',
                description='Initial step used to compute the similarity volume on Z axis (every N pixels on the epilolar line).\n'
                            '-1 means automatic estimation.\n'
                            'This value will be adjusted in all case to fit in the max memory (sgmMaxDepths).',
                value=-1,
                range=(-1, 10, 1),
                uid=[0],
            ),
            desc.IntParam(
                name='sgmMaxTCamsPerTile',
                label='Max Nb Neighbour Cameras Per Tile',
                description='Maximum number of neighbour cameras used per tile.',
                value=4,
                range=(1, 20, 1),
                uid=[0],
            ),
            desc.IntParam(
                name='sgmWSH',
                label='WSH',
                description='Half-size of the patch used to compute the similarity. Patch width is wsh*2+1.',
                value=4,
                range=(1, 20, 1),
                uid=[0],
                advanced=True,
            ),
            desc.BoolParam(
                name='sgmUseSfmSeeds',
                label='Use SfM Landmarks',
                description='Use landmarks from Structure-from-Motion as input seeds to define min/max depth ranges.',
                value=True,
                uid=[0],
                advanced=True,
            ),
            desc.FloatParam(
                name='sgmSeedsRangeInflate',
                label='Seeds Range Inflate',
                description='Inflate factor to add margins around SfM seeds.',
                value=0.2,
                range=(0.0, 2.0, 0.1),
                uid=[0],
                advanced=True,
            ),
            desc.FloatParam(
                name='sgmGammaC',
                label='GammaC',
                description='GammaC threshold used for similarity computation.',
                value=5.5,
                range=(0.0, 30.0, 0.5),
                uid=[0],
                advanced=True,
            ),
            desc.FloatParam(
                name='sgmGammaP',
                label='GammaP',
                description='GammaP threshold used for similarity computation.',
                value=8.0,
                range=(0.0, 30.0, 0.5),
                uid=[0],
                advanced=True,
            ),
            desc.FloatParam(
                name='sgmP1',
                label='P1',
                description='P1 parameter for SGM filtering.',
                value=10.0,
                range=(0.0, 255.0, 0.5),
                uid=[0],
                advanced=True,
            ),
            desc.FloatParam(
                name='sgmP2Weighting',
                label='P2 Weighting',
                description='P2 weighting parameter for SGM filtering.',
                value=100.0,
                range=(-255.0, 255.0, 0.5),
                uid=[0],
                advanced=True,
            ),
            desc.IntParam(
                name='sgmMaxDepths',
                label='Max Depths',
                description='Maximum number of depths in the similarity volume.',
                value=1500,
                range=(1, 5000, 1),
                uid=[0],
                advanced=True,
            ),
            desc.StringParam(
                name='sgmFilteringAxes',
                label='Filtering Axes',
                description='Define axes for the filtering of the similarity volume.',
                value='YX',
                uid=[0],
                advanced=True,
            ),
            desc.BoolParam(
                name='sgmDepthListPerTile',
                label='Depth List Per Tile',
                description='Select the list of depth planes per tile or globally to the image.',
                value=True,
                uid=[0],
                advanced=True,
            ),
        ]),
        desc.GroupAttribute(
            name='refine',
            label='Refine',
            description='The refine step computes a similarity volume in higher resolution but with a small depth range around the SGM depth map.\n'
                        'This allows to compute a depth map with sub-pixel accuracy.',
            group=None,
            groupDesc=[
            desc.BoolParam(
                name='refineEnabled',
                label='Enable',
                description='Enable depth/similarity map refinement process.',
                value=True,
                uid=[0],
            ),
            desc.IntParam(
                name='refineScale',
                label='Downscale factor',
                description='Downscale factor applied on source images for the Refine step (in addition to the global downscale).',
                value=1,
                range=(-1, 10, 1),
                uid=[0],
                enabled= lambda node: node.refine.refineEnabled.value,
            ),
            desc.IntParam(
                name='refineStepXY',
                label='Step XY',
                description='The step is used to compute the refine volume for one pixel over N (in the XY image plane).',
                value=1,
                range=(-1, 10, 1),
                uid=[0],
                enabled= lambda node: node.refine.refineEnabled.value,
            ),
            desc.IntParam(
                name='refineMaxTCamsPerTile',
                label='Max Nb Neighbour Cameras Per Tile',
                description='Maximum number of neighbour cameras used per tile.',
                value=4,
                range=(1, 20, 1),
                uid=[0],
                enabled= lambda node: node.refine.refineEnabled.value,
            ),
            desc.IntParam(
                name='refineSubsampling',
                label='Number of Subsamples',
                description='The number of subsamples used to extract the best depth from the refine volume (sliding gaussian window precision).',
                value=10,  
                range=(1, 30, 1),
                uid=[0],
                advanced=True,
                enabled= lambda node: node.refine.refineEnabled.value,
            ),
            desc.IntParam(
                name='refineHalfNbDepths',
                label='Half Number of Depths',
                description='The thickness of the refine area around the initial depth map.\n'
                            'This parameter defines the number of depths in front of and behind the initial value \n'
                            'for which we evaluate the similarity with a finer z sampling.',
                value=15,
                range=(1, 50, 1),
                uid=[0],
                advanced=True,
                enabled= lambda node: node.refine.refineEnabled.value,
            ),
            desc.IntParam(
                name='refineWSH',
                label='WSH',
                description='Half-size of the patch used to compute the similarity. Patch width is wsh*2+1.',
                value=3,
                range=(1, 20, 1),
                uid=[0],
                advanced=True,
                enabled= lambda node: node.refine.refineEnabled.value,
            ),
            desc.FloatParam(
                name='refineSigma',
                label='Sigma',
                description='Sigma (2*sigma^2) of the gaussian filter used to extract the best depth from the refine volume.',
                value=15.0,
                range=(0.0, 30.0, 0.5),
                uid=[0],
                advanced=True,
                enabled= lambda node: node.refine.refineEnabled.value,
            ),
            desc.FloatParam(
                name='refineGammaC',
                label='GammaC',
                description='GammaC threshold used for similarity computation.',
                value=15.5,
                range=(0.0, 30.0, 0.5),
                uid=[0],
                advanced=True,
                enabled= lambda node: node.refine.refineEnabled.value,
            ),
            desc.FloatParam(
                name='refineGammaP',
                label='GammaP',
                description='GammaP threshold used for similarity computation.',
                value=8.0,
                range=(0.0, 30.0, 0.5),
                uid=[0],
                advanced=True,
                enabled= lambda node: node.refine.refineEnabled.value,
            ),
        ]),
        desc.GroupAttribute(
            name="colorOptimization",
            label="Color Optimization",
            description='Color optimization post-process parameters.',
            group=None,
            groupDesc=[
            desc.BoolParam(
                name='colorOptimizationEnabled',
                label='Enable',
                description='Enable depth/similarity map post-process color optimization.', 
                value=True,
                uid=[0],
            ),
            desc.IntParam(
                name='colorOptimizationNbIterations',
                label='Number of Iterations',
                description='Number of iterations of the optimization.',
                value=100,
                range=(1, 500, 10),
                uid=[0],
                advanced=True,
                enabled= lambda node: node.colorOptimization.colorOptimizationEnabled.value,
            ),
        ]),
        desc.GroupAttribute(
            name='intermediateResults',
            label='Intermediate Results',
            description='Intermediate results parameters for debug purposes.\n'
                        'Warning: Dramatically affect performances and use large amount of storage.',
            advanced=True,
            group=None,
            groupDesc=[
            desc.BoolParam(
                name='exportIntermediateDepthSimMaps',
                label='Export Depth Maps',
                description='Export intermediate depth/similarity maps from the SGM and Refine steps.',
                value=False,
                uid=[],
                advanced=True,
            ),
            desc.BoolParam(
                name='exportIntermediateVolumes',
                label='Export Volumes',
                description='Export intermediate full similarity volumes from the SGM and Refine steps.',
                value=False,
                uid=[],
                advanced=True,
            ),
            desc.BoolParam(
                name='exportIntermediateCrossVolumes',
                label='Export Cross Volumes',
                description='Export intermediate similarity cross volumes from the SGM and Refine steps.',
                value=False,
                uid=[],
                advanced=True,
            ),
            desc.BoolParam(
                name='exportIntermediateVolume9pCsv',
                label='Export 9 Points',
                description='Export intermediate volumes 9 points from the SGM and Refine steps in CSV files.',
                value=False,
                uid=[],
                advanced=True,
            ),
            desc.BoolParam(
                name='exportTilePattern',
                label='Export Tile Pattern',
                description='Export the bounding boxes of tiles volumes as meshes. This allows to visualize the depth map search areas.',
                value=False,
                uid=[],
                advanced=True,
            ),
        ]),
        desc.IntParam(
            name='nbGPUs',
            label='Number of GPUs',
            description='Number of GPUs to use (0 means use all available GPUs).',
            value=0,
            range=(0, 5, 1),
            uid=[],
            advanced=True,
        ),
        desc.ChoiceParam(
            name='verboseLevel',
            label='Verbose Level',
            description='''verbosity level (fatal, error, warning, info, debug, trace).''',
            value='info',
            values=['fatal', 'error', 'warning', 'info', 'debug', 'trace'],
            exclusive=True,
            uid=[],
        ),
    ]

    outputs = [
        desc.File(
            name='output',
            label='Folder',
            description='Output folder for generated depth maps.',
            value=desc.Node.internalFolder,
            uid=[],
        ),
        # these attributes are only here to describe more accurately the output of the node
        # by specifying that it generates 2 sequences of images
        # (see in Viewer2D.qml how these attributes can be used)
        desc.File(
            name='depth',
            label='Depth Maps',
            description='Generated depth maps.',
            semantic='image',
            value=desc.Node.internalFolder + '<VIEW_ID>_depthMap.exr',
            uid=[],
            group='', # do not export on the command line
        ),
        desc.File(
            name='sim',
            label='Sim Maps',
            description='Generated sim maps.',
            semantic='image',
            value=desc.Node.internalFolder + '<VIEW_ID>_simMap.exr',
            uid=[],
            group='', # do not export on the command line
        ),
        desc.File(
            name='tilePattern',
            label='Tile Pattern',
            description='Debug: Tile pattern',
            value=desc.Node.internalFolder + '<VIEW_ID>_tilePattern.obj',
            uid=[],
            group='', # do not export on the command line
            # enabled=lambda node: node.intermediateResults.exportTilePattern.value,
        ),
        desc.File(
            name='depthSgm',
            label='Depth Maps SGM',
            description='Debug: Depth maps SGM',
            semantic='image',
            value=desc.Node.internalFolder + '<VIEW_ID>_depthMap_scale2_sgm.exr',
            uid=[],
            group='', # do not export on the command line
            # enabled=lambda node: node.intermediateResults.exportIntermediateDepthSimMaps.value,
        ),
        desc.File(
            name='depthSgmUpscaled',
            label='Depth Maps SGM Upscaled',
            description='Debug: Depth maps SGM upscaled',
            semantic='image',
            value=desc.Node.internalFolder + '<VIEW_ID>_depthMap_sgmUpscaled.exr',
            uid=[],
            group='', # do not export on the command line
            # enabled=lambda node: node.intermediateResults.exportIntermediateDepthSimMaps.value,
        ),
        desc.File(
            name='depthRefined',
            label='Depth Maps Refined',
            description='Debug: Depth maps after refinement',
            semantic='image',
            value=desc.Node.internalFolder + '<VIEW_ID>_depthMap_refinedFused.exr',
            uid=[],
            group='', # do not export on the command line
            # enabled=lambda node: node.intermediateResults.exportIntermediateDepthSimMaps.value,
        ),
    ]
