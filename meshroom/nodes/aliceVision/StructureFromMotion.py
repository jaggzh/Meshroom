__version__ = "2.0"

from meshroom.core import desc


class StructureFromMotion(desc.AVCommandLineNode):
    commandLine = 'aliceVision_incrementalSfM {allParams}'
    size = desc.DynamicNodeSize('input')

    category = 'Sparse Reconstruction'
    documentation = '''
This node will analyze feature matches to understand the geometric relationship behind all the 2D observations,
and infer the rigid scene structure (3D points) with the pose (position and orientation) and internal calibration of all cameras.
The pipeline is a growing reconstruction process (called incremental SfM): it first computes an initial two-view reconstruction that is iteratively extended by adding new views.

1/ Fuse 2-View Matches into Tracks

It fuses all feature matches between image pairs into tracks. Each track represents a candidate point in space, visible from multiple cameras.
However, at this step of the pipeline, it still contains many outliers.

2/ Initial Image Pair

It chooses the best initial image pair. This choice is critical for the quality of the final reconstruction.
It should indeed provide robust matches and contain reliable geometric information.
So, this image pair should maximize the number of matches and the repartition of the corresponding features in each image.
But at the same time, the angle between the cameras should also be large enough to provide reliable geometric information.

3/ Initial 2-View Geometry

It computes the fundamental matrix between the 2 images selected and consider that the first one is the origin of the coordinate system.

4/ Triangulate

Now with the pose of the 2 first cameras, it triangulates the corresponding 2D features into 3D points.

5/ Next Best View Selection

After that, it selects all the images that have enough associations with the features that are already reconstructed in 3D.

6/ Estimate New Cameras

Based on these 2D-3D associations it performs the resectioning of each of these new cameras.
The resectioning is a Perspective-n-Point algorithm (PnP) in a RANSAC framework to find the pose of the camera that validates most of the features associations.
On each camera, a non-linear minimization is performed to refine the pose.

7/ Triangulate

From these new cameras poses, some tracks become visible by 2 or more resected cameras and it triangulates them.

8/ Optimize

It performs a Bundle Adjustment to refine everything: extrinsics and intrinsics parameters of all cameras as well as the position of all 3D points.
It filters the results of the Bundle Adjustment by removing all observations that have high reprojection error or insufficient angles between observations.

9/ Loop from 5 to 9

As we have triangulated new points, we get more image candidates for next best views selection and we can iterate from 5 to 9.
It iterates like that, adding cameras and triangulating new 2D features into 3D points and removing 3D points that became invalidated, until we cannot localize new views.

## Online
[https://alicevision.org/#photogrammetry/sfm](https://alicevision.org/#photogrammetry/sfm)
'''

    inputs = [
        desc.File(
            name='input',
            label='SfMData',
            description='SfMData file.',
            value='',
            uid=[0],
        ),
        desc.ListAttribute(
            elementDesc=desc.File(
                name="featuresFolder",
                label="Features Folder",
                description="",
                value="",
                uid=[0],
            ),
            name="featuresFolders",
            label="Features Folders",
            description="Folder(s) containing the extracted features and descriptors."
        ),
        desc.ListAttribute(
            elementDesc=desc.File(
                name="matchesFolder",
                label="Matches Folder",
                description="",
                value="",
                uid=[0],
            ),
            name="matchesFolders",
            label="Matches Folders",
            description="Folder(s) in which computed matches are stored."
        ),
        desc.ChoiceParam(
            name='describerTypes',
            label='Describer Types',
            description='The algorithm used to extract distinctive features from images.\n'
                        'sift: Popular method for detecting/describing features.\n'
                        '      Robust to changes in scale and orientation\n'
                        ' sift_float: Uses floats (not ints).\n'
                        ' sift_upright: Variation that does not compute scale and orientation.\n'
                        ' dspsift: Dense version of SIFT that samples features at regular intervals.\n'
                        '      (More efficient, but may be less accurate.)\n'
                        'akaze: A faster and more memory-efficient alternative to SIFT.\n'
                        '      Less sensitive to affine distortion, making it useful for changing camera perspectives.\n'
                        '      (Good to use in combination with SIFT)\n'
                        ' akaze_liop: With Local Intensity Order Pattern features.\n'
                        ' akaze_mldb: With Multi-Learning Decision Binary features.\n'
                        'cctag3: Features for detecting Cube-Circle-Triangle markers in images.\n'
                        '      Robust to changes in illumination and scale, and can be used to estimate camera pose.\n'
                        'cctag4: Variation of CCTAG with more information in markers.\n'
                        'sift_ocv: Implementation of SIFT provided by OpenCV.\n'
                        'akaze_ocv: Implementation of AKAZE provided by OpenCV.\n'
                        'tag16h5: Features for detecting AprilTag markers in images.\n'
                        '      Robust and reliable for object detection and pose estimation.',
            value=['dspsift'],
            values=['sift', 'sift_float', 'sift_upright', 'dspsift', 'akaze', 'akaze_liop', 'akaze_mldb', 'cctag3', 'cctag4', 'sift_ocv', 'akaze_ocv', 'tag16h5'],
            exclusive=False,
            uid=[0],
            joinChar=',',
        ),
Please also describe the values, adding the descriptions ton the description=
        desc.ChoiceParam(
            name='localizerEstimator',
            label='Localizer Estimator',
            description='The type of estimator used to localize cameras. '
                        '(The algorithm used to find the best estimate for the camera positions and orientations.)\n'
                        'acransac: Efficient RANSAC algorithm that uses pre-conditioning and early termination.\n'
                        'ransac: Standard RANSAC algorithm for estimating model parameters from data.\n'
                        'lsmeds: Least-Median-of-Squares (LMedS) algorithm for robust estimation.\n'
                        'loransac: LO-RANSAC algorithm that combines RANSAC and LMedS.\n'
                        'maxconsensus: Maximum Consensus (MC) algorithm for robust estimation.',
            value='acransac',
            values=['acransac', 'ransac', 'lsmeds', 'loransac', 'maxconsensus'],
            exclusive=True,
            uid=[0],
            advanced=True,
        ),
        desc.ChoiceParam(
            name='observationConstraint',
            label='Observation Constraint',
            description='Observation constraint mode used in the optimization:\n'
                        ' * Basic: Use standard reprojection error in pixel coordinates\n'
                        ' * Scale: Use reprojection error in pixel coordinates but relative to the feature scale',
            value='Scale',
            values=['Basic', 'Scale'],
            exclusive=True,
            uid=[0],
            advanced=True,
        ),
        desc.IntParam(
            name='localizerEstimatorMaxIterations',
            label='Localizer Max Ransac Iterations',
            description='Maximum number of iterations allowed in ransac step.',
            value=4096,
            range=(1, 20000, 1),
            uid=[0],
            advanced=True,
        ),
        desc.FloatParam(
            name='localizerEstimatorError',
            label='Localizer Max Ransac Error',
            description='Maximum error (in pixels) allowed for camera localization (resectioning).\n'
                        'If set to 0, it will select a threshold according to the localizer estimator used\n'
                        '(if ACRansac, it will analyze the input data to select the optimal value).',
            value=0.0,
            range=(0.0, 100.0, 0.1),
            uid=[0],
            advanced=True,
        ),
       desc.BoolParam(
            name='lockScenePreviouslyReconstructed',
            label='Lock Scene Previously Reconstructed',
            description='This option is useful for SfM augmentation. Lock previously reconstructed poses and intrinsics.',
            value=False,
            uid=[0],
        ),
        desc.BoolParam(
            name='useLocalBA',
            label='Local Bundle Adjustment',
            description='It reduces the reconstruction time, especially for large datasets (500+ images),\n'
                        'by avoiding computation of the Bundle Adjustment on areas that are not changing.',
            value=True,
            uid=[0],
        ),
        desc.IntParam(
            name='localBAGraphDistance',
            label='LocalBA Graph Distance',
            description='Graph-distance limit to define the Active region in the Local Bundle Adjustment strategy.',
            value=1,
            range=(2, 10, 1),
            uid=[0],
            advanced=True,
        ),
        desc.IntParam(
            name='maxNumberOfMatches',
            label='Maximum Number of Matches',
            description='Maximum number of matches per image pair (and per feature type). \n'
                        'This can be useful to have a quick reconstruction overview. \n'
                        '0 means no limit.',
            value=0,
            range=(0, 50000, 1),
            uid=[0],
        ),
        desc.IntParam(
            name='minNumberOfMatches',
            label='Minimum Number of Matches',
            description='Minimum number of matches per image pair (and per feature type). \n'
                        'This can be useful to have a meaningful reconstruction with accurate keypoints. 0 means no limit.',
            value=0,
            range=(0, 50000, 1),
            uid=[0],
        ),
        desc.IntParam(
            name='minInputTrackLength',
            label='Min Input Track Length',
			description='Minimum track length to be used as input of the SfM (Structure from\n'
						'Motion) process. A track is a set of features in different images\n'
						'that correspond to the same 3D point. By setting this parameter to a\n'
						'higher value, shorter tracks that are less reliable or contain outliers\n'
						'can be ignored, which can improve the accuracy and reliability of the\n'
						'reconstruction. However, setting this parameter too high can also result\n'
						'in a loss of information and potentially lead to missing or incomplete\n'
						'reconstructions.',
            value=2,
            range=(2, 10, 1),
            uid=[0],
        ),
        desc.IntParam(
            name='minNumberOfObservationsForTriangulation',
            label='Min Observation For Triangulation',
            description='Minimum number of observations to triangulate a point.\n'
                        'Set it to 3 (or more) reduces drastically the noise in the point cloud,\n'
                        'but the number of final poses is a little bit reduced\n'
                        '(from 1.5% to 11% on the tested datasets).',
            value=2,
            range=(2, 10, 1),
            uid=[0],
            advanced=True,
        ),
        desc.FloatParam(
            name='minAngleForTriangulation',
            label='Min Angle For Triangulation',
            description='This parameter sets the minimum angle required between two views to perform triangulation. '
                        'Triangulation is the process of determining the 3D position of a point based on its projections in '
                        'two or more views. A higher value for this parameter can improve the accuracy of the reconstruction, '
                        'but may also reduce the number of points that can be triangulated.',
            value=3.0,
            range=(0.1, 10.0, 0.1),
            uid=[0],
            advanced=True,
        ),
        desc.FloatParam(
            name='minAngleForLandmark',
            label='Min Angle For Landmark',
            description='This parameter sets the minimum angle required between two views to create a landmark. A landmark is '
                        'a point that is manually marked in multiple images to help improve the reconstruction accuracy. '
                        'A higher value for this parameter can reduce the number of landmarks created, but may also improve '
                        'the overall accuracy of the reconstruction.',
            value=2.0,
            range=(0.1, 10.0, 0.1),
            uid=[0],
            advanced=True,
        ),
        desc.FloatParam(
            name='maxReprojectionError',
            label='Max Reprojection Error',
            description='This parameter sets the maximum allowable reprojection error for triangulated points. Reprojection '
                        'error is a measure of the accuracy of the 3D reconstruction and is calculated as the distance '
                        'between the projection of a 3D point onto an image and the corresponding 2D point in that image. '
                        'A lower value for this parameter can improve the accuracy of the reconstruction, but may also '
                        'reduce the number of points that can be triangulated.',
            value=4.0,
            range=(0.1, 10.0, 0.1),
            uid=[0],
            advanced=True,
        ),
        desc.FloatParam(
            name='minAngleInitialPair',
            label='Min Angle Initial Pair',
            description='This parameter sets the minimum angle required between the two views used to create the initial pair. '
                        'The initial pair is the first pair of images used to start the reconstruction process. A higher '
                        'value for this parameter can improve the accuracy of the initial pair, but may also limit the number '
                        'of images that can be used for reconstruction.',
            value=5.0,
            range=(0.1, 10.0, 0.1),
            uid=[0],
            advanced=True,
        ),
        desc.FloatParam(
            name='maxAngleInitialPair',
            label='Max Angle Initial Pair',
            description='This parameter sets the maximum angle allowed between the two views used to create the initial pair. '
                        'A higher value for this parameter can increase the number of images that can be used for '
                        'reconstruction, but may also reduce the accuracy of the initial pair.',
            value=40.0,
            range=(0.1, 60.0, 0.1),
            uid=[0],
            advanced=True,
        ),
        desc.BoolParam(
            name='useOnlyMatchesFromInputFolder',
            label='Use Only Matches From Input Folder',
            description='This parameter determines whether only matches from the input matchesFolder will be used for '
                        'reconstruction, or if matches from previously added folders in the SfMData file will also be used.',
            value=False,
            uid=[],
            advanced=True,
        ),
        desc.BoolParam(
            name='useRigConstraint',
            label='Use Rig Constraint',
            description='This parameter enables or disables the use of rig constraints during reconstruction. '
                        'Rig constraints are used to enforce certain geometric relationships between the cameras in a '
                        'multi-camera system.',
            value=True,
            uid=[0],
            advanced=True,
        ),
        desc.IntParam(
            name='rigMinNbCamerasForCalibration',
            label='Min Nb Cameras For Rig Calibration',
            description='This parameter sets the minimal number of cameras required to start the calibration of the rig. '
                        'The rig calibration process determines the relative positions and orientations of the cameras '
                        'in a multi-camera system.',
            value=20,
            range=(1, 50, 1),
            uid=[0],
            advanced=True,
        ),
        desc.BoolParam(
            name='lockAllIntrinsics',
            label='Force Lock of All Intrinsic Camera Parameters',
            description='Force to keep constant all the intrinsics parameters of the cameras (focal length, \n'
                        'principal point, distortion if any) during the reconstruction.\n'
                        'This may be helpful if the input cameras are already fully calibrated.',
            value=False,
            uid=[0],
        ),
        desc.IntParam(
            name='minNbCamerasToRefinePrincipalPoint',
            label='Min Nb Cameras To Refine Principal Point',
            description='Minimal number of cameras to refine the principal point of the cameras (one of the intrinsic parameters of the camera). '
                        'If we do not have enough cameras, the principal point in consider is considered in the center of the image. '
                        'If minNbCamerasToRefinePrincipalPoint<=0, the principal point is never refined. '
                        'If minNbCamerasToRefinePrincipalPoint==1, the principal point is always refined.',
            value=3,
            range=(0, 20, 1),
            uid=[0],
            advanced=True,
        ),
        desc.BoolParam(
            name='filterTrackForks',
            label='Filter Track Forks',
            description='Enable/Disable the track forks removal. A track contains a fork when incoherent matches \n'
                        'lead to multiple features in the same image for a single track. \n',
            value=False,
            uid=[0],
        ),
        desc.BoolParam(
            name='computeStructureColor',
            label='Compute Structure Color',
            description='Enable/Disable color computation of each 3D point.',
            value=True,
            uid=[0],
        ),
        desc.File(
            name='initialPairA',
            label='Initial Pair A',
            description='Filename of the first image (without path).',
            value='',
            uid=[0],
        ),
        desc.File(
            name='initialPairB',
            label='Initial Pair B',
            description='Filename of the second image (without path).',
            value='',
            uid=[0],
        ),
        desc.ChoiceParam(
            name='interFileExtension',
            label='Inter File Extension',
            description='Extension of the intermediate file export.',
            value='.abc',
            values=('.abc', '.ply'),
            exclusive=True,
            uid=[],
            advanced=True,
        ),
        desc.ChoiceParam(
            name='verboseLevel',
            label='Verbose Level',
            description='Verbosity level (fatal, error, warning, info, debug, trace).',
            value='info',
            values=['fatal', 'error', 'warning', 'info', 'debug', 'trace'],
            exclusive=True,
            uid=[],
        )
    ]

    outputs = [
        desc.File(
            name='output',
            label='SfMData',
            description='Path to the output sfmdata file',
            value=desc.Node.internalFolder + 'sfm.abc',
            uid=[],
        ),
        desc.File(
            name='outputViewsAndPoses',
            label='Views and Poses',
            description='''Path to the output sfmdata file with cameras (views and poses).''',
            value=desc.Node.internalFolder + 'cameras.sfm',
            uid=[],
        ),
        desc.File(
            name='extraInfoFolder',
            label='Folder',
            description='Folder for intermediate reconstruction files and additional reconstruction information files.',
            value=desc.Node.internalFolder,
            uid=[],
        ),
    ]
