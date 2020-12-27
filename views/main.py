"""
Views to interact with flask server
"""
from flask import Blueprint, jsonify, request, make_response
from kcomp import *
# import cv2
# import itertools
# import os
# import numpy as np
# import openface
# import time

MAIN_BLUEPRINT = Blueprint("main", __name__)

print("Starting using config: ")
print(args)
# start = time.time()
# align = openface.AlignDlib(args.dlibFacePredictor)
# net = openface.TorchNeuralNet(args.networkModel, args.imgDim)
# if verbose:
#     print("Loading the dlib and OpenFace models took {} seconds.".format(
#         time.time() - start))

def getRep(fileStream, filename):
    if args.verbose:
        print("Processing {}.".format(filename))
    img_array = np.fromstring(fileStream.read(), np.uint8)
    bgrImg = cv2.imdecode(img_array, cv2.CV_LOAD_IMAGE_UNCHANGED)

    # bgrImg = cv2.imread(imgPath)
    if bgrImg is None:
        raise Exception("Unable to load image: {}".format(filename))
    rgbImg = cv2.cvtColor(bgrImg, cv2.COLOR_BGR2RGB)

    if args.verbose:
        print("  + Original size: {}".format(rgbImg.shape))

    start = time.time()
    bb = align.getLargestFaceBoundingBox(rgbImg)
    if bb is None:
        raise Exception("Unable to find a face: {}".format(filename))
    if args.verbose:
        print("  + Face detection took {} seconds.".format(time.time() - start))

    start = time.time()
    alignedFace = align.align(args.imgDim, rgbImg, bb,
                              landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
    if alignedFace is None:
        raise Exception("Unable to align image: {}".format(filename))
    if args.verbose:
        print("  + Face alignment took {} seconds.".format(time.time() - start))

    start = time.time()
    rep = net.forward(alignedFace)
    if args.verbose:
        print("  + OpenFace forward pass took {} seconds.".format(time.time() - start))
        # print("Representation:")
        # print(rep)
        # print("-----\n")
    return rep

@MAIN_BLUEPRINT.route("/health", methods=["GET"])
def get_health():
    """
    Check health of the service

    Returns:
        Health status of the service
    """
    print 'health'
    return "OK"


@MAIN_BLUEPRINT.route("/post_imgs", methods=["POST", "OPTIONS"])
def post_images():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_prelight_response()
    elif request.method == "POST": # The actual request following the preflight
        imgs_list = request.files.getlist("imgs[]")
        print("imgs_list")
        # names = [f.filename for f in imgs_list]
        print(imgs_list)
        output = {"msg": get_distances(imgs_list)}
        return _corsify_actual_response(output)
    else:
        raise RuntimeError("Weird - don't know how to handle method {}".format(request.method))
    print('finished')

def _build_cors_prelight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def _corsify_actual_response(output):
    response = jsonify(output)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

def get_distances(img_list):
    if not len(img_list) >= 2:
        print("Error: must compare 2 or more images")
        return
    img1 = img_list[0]
    img2 = img_list[1]
    d = getRep(img1, img1.filename) - getRep(img2, img2.filename)
    norm = "{:0.3f}".format(np.dot(d, d))
    return (img1.filename, img2.filename, norm)
