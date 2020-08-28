# py-vision
Machine Vision Solutions written in Python.

This Project contains two Image Processing solutions, Reconstructing an RGB Colour image from a Sinogram Projection and Image Stitching using the Harris Corner Detector.
Both solutions are written in Python 3 using libraries from Numpy, Scipy, PIL and Imutils. These libraries can be downloaded from PyPi.
This project was created to demonstrate the usability and functionality of Python to address modern Machine Vision problems. Neither the Sinogram Reconstruction
nor Image Stitching files were intended to be used as part of any tool or product in themselves - they demonstrate how one would solve a machine vision problem and may or
may not work for all files or formats.

Image Reconstruction from a Sinogram: This routine outlines the method for composite RGB Image reconstruction from the Sinogram of the image, which is also known as it’s 
Radon Transform. The Image used is a color test card. Reconstruction is carried out by code written for Python 3.0 (may not function on earlier versions). Routines from the 
NumPy and SciPy packages for Python are used to accelerate reconstruction performance, particularly matrix and tensor operations. 

Image Stitching using Harris Corner and Edge Detector: This routine outlines the method for Harris Corner detection on a pair of related images. These images are related by 
a translation and are composed into a mosaic through Image Stitching. The Harris Corner detector is used along with a Harris interest point descriptor to locate matching 
‘points of interest’ in both images. A translation matrix of these points is then filtered to find strongest point matches using the RANSAC (Random Sample Consensus) 
statistical technique. 

Both routines are an educational piece of code - they may not work everywhere and of course there may be better ways to implement this.
