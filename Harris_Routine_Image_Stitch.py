# Harris Corner Detector and Image Stitching Routine
# Input images must be .png files and located in working directory
# Modules used: Pylab, Numpy, Scipy, Imutils
# Ingar Filinn 2019
from pylab import *
from numpy import *
from scipy.ndimage import filters
import imutils


im_a1 = imutils.imread('balloon1.png', greyscale=True)
im_a2 = imutils.imread('balloon2.png', greyscale=True)
# Test routine for rotating images
# im_a1 = np.rot90(imset1, k=1)
# im_a2 = np.rot90(imset2, k=1)
# RGB Colour versions of images (if used)
a1RGB = imutils.imread('balloon1.png', greyscale=False)
a2RGB = imutils.imread('balloon2.png', greyscale=False)
im_min, im_max = im_a1.min(), im_a1.max()
row_1, col_1 = im_a1.shape
row_2, col_2 = im_a2.shape
# Status readouts (for DeBug only - not used)
# print(str(row_1))
# print(str(col_1))

# Functions...


def harris(im, sigma=3):
    # Harris Corner function using Harmonic Mean for feature Eigenvalue description
    # Calculate input image derivatives in x and y directions with sigma specified
    imx = zeros(im.shape)
    # Form Gaussian y derivative (col)
    filters.gaussian_filter(im, (sigma, sigma), (0, 1), imx)
    imy = zeros(im.shape)
    # Form Gaussian x derivative (row)
    filters.gaussian_filter(im, (sigma, sigma), (1, 0), imy)
    # Construct local structure matrix/tensor 'M'
    gxx = filters.gaussian_filter(imx * imx, sigma)
    gxy = filters.gaussian_filter(imx * imy, sigma)
    gyy = filters.gaussian_filter(imy * imy, sigma)
    # Harris Function "r" using Harmonic Mean
    # Calculate determinant and trace of Matrix 'M'
    g_det = gxx * gyy - gxy ** 2
    gtr = gxx + gyy
    return g_det / gtr


def interest_points(harrisim, min_dist=10, threshold=0.1):
    # Calcuate Harris Corner Interest points and perform non-max suppression on neighbours
    # Return filtered co-ordinates of unique match points
    # min_dist is the minimum number of pixels between the corners and image boundary
    corner_threshold = harrisim.max() * threshold
    harrisim_t = (harrisim > corner_threshold) * 1
    # get coordinates of candidates and their values
    coords = array(harrisim_t.nonzero()).T
    candidate_values = [harrisim[c[0], c[1]] for c in coords]
    # sort candidates
    index = argsort(candidate_values)[::-1]
    # store allowed point locations in a boolean array called 'allowed locations'
    allowed_locations = zeros(harrisim.shape)
    allowed_locations[min_dist:-min_dist, min_dist:-min_dist] = 1
    # Select candidates using min_distance between each co-ordinate
    filtered_coords = []
    for i in index:
        if allowed_locations[coords[i, 0], coords[i, 1]] == 1:
            filtered_coords.append(coords[i])
            allowed_locations[(coords[i, 0] - min_dist):(coords[i, 0] + min_dist),
            (coords[i, 1] - min_dist):(coords[i, 1] + min_dist)] = 0
    return filtered_coords


def plot_harris_points(image, filtered_coords):
    # Create new graph using 'pyplot' and plot filtered co-ordinates as Harris interest points
    # Create new figure
    figure()
    gray()
    imshow(image)
    plot([p[1] for p in filtered_coords],
         [p[0] for p in filtered_coords], '+')
    axis('off')
    show()


def normalize(image, filtered_coords, wid=5):
    # Calculate intensities of pixel change around each interest point inside patch window
    # Create a list object to store patch descriptors for analysis called 'pds'
    pds = []
    for coords in filtered_coords:
        # Patch to Vector
        patch = image[coords[0] - wid:coords[0] + wid + 1, coords[1] - wid:coords[1] + wid + 1].flatten()
        pds.append(patch)
    return pds


def match(descriptor1, descriptor2, threshold=0.5):
    # Perform interest point matching between points in 'HIPS' in Image 1 and 'HIPS' in Image 2
    n = len(descriptor1[0])
    # Distances between corresponding image pairs
    d = -ones((len(descriptor1), len(descriptor2)))
    for i in range(len(descriptor1)):
        for j in range(len(descriptor2)):
            d1 = (descriptor1[i] - mean(descriptor1[i])) / std(descriptor1[i])
            d2 = (descriptor2[j] - mean(descriptor2[j])) / std(descriptor2[j])
            ncc_value = sum(d1 * d2) / (n - 1)
            if ncc_value > threshold:
                d[i, j] = ncc_value
    # Sort values by maximum first using numpy's 'argsort' function
    dxdy = argsort(-d)
    matchscores = dxdy[:, 0]
    return matchscores


def plot_symmetric(desc_1, desc_2, threshold=0.5):
    # Perform a match of the HIPS where both images are perfectly symmetrical
    # This is only needed for efficiency as it removes obviously bad translations
    matches_xy = match(desc_1, desc_2, threshold)
    matches_yx = match(desc_2, desc_1, threshold)
    dxy = where(matches_xy >= 0)[0]
    # remove non-symmetric translations between mapping points
    for n in dxy:
        if matches_yx[matches_xy[n]] != n:
            matches_xy[n] = -1
    return matches_xy


def collate_ims(im1, im2):
    # Create a new array and paste Images 1 and 2 into single image set for match comparison.
    rows1 = im1.shape[0]
    rows2 = im2.shape[0]
    # Set shape of new 'empty' array of zeros by adjusting it to the image with the largest
    # row, column sizes. Both remain equal if row, column are the same for both Images.
    if rows1 < rows2:
        im1 = concatenate((im1, zeros((rows2 - rows1, im1.shape[1]))), axis=0)
    elif rows1 > rows2:
        im2 = concatenate((im2, zeros((rows1 - rows2, im2.shape[1]))), axis=0)
    return concatenate((im1, im2), axis=1)


def plot_points(im1, im2, locs1, locs2, matchscores, show_below=True):  # Plots the matches between both images
    im3 = collate_ims(im1, im2)
    if show_below:
        im3 = vstack((im3, im3))
    imutils.imshow(im3)
    cols1 = im1.shape[1]
    for i, m in enumerate(matchscores):
        if m > 0:
            plot([locs1[i][1], locs2[m][1] + cols1], [locs1[i][0], locs2[m][0]], 'r')
    axis('off')


def mosaic(im1, im2, translation):
    # Perform image stitching by collating Image 1 and Image 2 into a new image at the
    # Offsets specified in 'translation'.
    # N.B - Print statement used for DeBug only
    # print(str(translation))
    # Create new array of zeros of size 'Image 1' + absolute value of 'Translation 1', etc.
    row_size = (im1.shape[0] + abs(translation[0]))
    col_size = (im1.shape[1] + abs(translation[1]))
    palette = np.zeros([row_size, col_size])
    palette[abs(translation[0]):row_size, 0:im1.shape[0]] = im1
    palette[0:im2.shape[1], abs(translation[1]):col_size] = im2
    # Display the output mosaic image
    imutils.imshow(palette)


def RANSAC(im1, locs1, locs2, matchscores):
    # Perform exhaustive RANSAC on all translations to give single best candidate translation
    sets = []
    translations = []
    agreements = []
    cols1 = im1.shape[1]
    # Calculate row, col differences for each translation in list of matches and append to 'sets'
    for i, m in enumerate(matchscores):
        if m > 0:
            rc_points = ([locs1[i][1], locs2[m][1] + cols1], [locs1[i][0], locs2[m][0]])
            for j in rc_points:
                diffs = (rc_points[0][0] - rc_points[1][0], rc_points[0][1] - rc_points[1][1])
                sets.append(diffs)
    # Calculate the Euclidian distance per point against all others and append to 'errors'
    for k in sets:
        errors = []
        candidates = []
        for l in sets:
            euclidian = abs((((k[0] - l[0]) * 2) + ((k[1] - l[1]) * 2)))
            # print(str(euclidian))
            errors.append(euclidian)
        # Filter out errors that are greater than 1.6 pixels. Append remainder to 'candidates'
        for n in errors:
            if abs(n) <= 1.6:
                candidates.append(n)
        # Count number of agreements in 'args' to measure amount of support per translation
        args = len(candidates)
        if args >= 2:
            agreements.append(args)
        # Need to append a zero in place of no agreements to preserve list index numbering
        else:
            agreements.append(0)
    index_tr = max(agreements)
    # print(str(index_tr))
    translations = sets[index_tr]
    # Return the translation that corresponds to the entry with the max number of agreements
    return translations


# Main sequence

# Set Size of Gaussian Window Kernel to 11 x 11 pixels
win_size = 11
# Step 1 - Threshold Harris images by applying Gaussian filter
hr_image = harris(im_a1, 1)
filtered_coords1 = interest_points(hr_image, win_size + 1)
# Step 2 - Form Normalized patch descriptor vectors
im1_d = normalize(im_a1, filtered_coords1, win_size)
hr_image = harris(im_a2, 1)
# Step 3 - Build response matrix and perform non-max suppression
filtered_coords2 = interest_points(hr_image, win_size + 1)
im2_d = normalize(im_a2, filtered_coords2, win_size)
# Plot matches on Images side-by-side
matches = plot_symmetric(im1_d, im2_d)
# Step 4 - Perform exhaustive RANSAC to filter outliers and return best fit
# Main Image stitching sequence
match_points = RANSAC(im_a1, filtered_coords1, filtered_coords2, matches)
# Step 5 - Plot a mosaic of Images using translation to complete Image Stitching
mosaic(im_a1, im_a2, match_points)
print("End")
