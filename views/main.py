"""
Views to interact with flask server
"""
from flask import Blueprint, jsonify, request, make_response, abort
from kcomp import *

MAIN_BLUEPRINT = Blueprint("main", __name__)


def getRep(fileStream):
    filename = fileStream.filename
    if args.verbose:
        print("Processing {}.".format(filename))
    img_array = np.fromstring(fileStream.read(), np.uint8)
    # bgrImg = cv2.imread(imgPath)
    bgrImg = cv2.imdecode(img_array, cv2.CV_LOAD_IMAGE_UNCHANGED)

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
    
    # write_img(alignedFace, filename)
    start = time.time()
    rep = net.forward(alignedFace)
    if args.verbose:
        print("  + OpenFace forward pass took {} seconds.".format(time.time() - start))
    return rep

def write_img(img_array, filename):
    file_parts = filename.split(".")
    outfile = file_parts[0] + "_align"
    # Append extension if exists
    if len(file_parts) > 1:
        outfile += "." + file_parts[1]
    SAVE_DIR = "k_photos/aligned/"
    ## Note, above is misguided. we MUST have an extension, for imwrite to choose format
    cv2.imwrite(SAVE_DIR + outfile, img_array)
    if args.verbose:
        print("  Saving aligned face to: {}".format(outfile))

@MAIN_BLUEPRINT.route("/health", methods=["GET"])
def get_health():
    """
    Check health of the service

    Returns:
        Health status of the service
    """
    print('health')
    return "OK"


@MAIN_BLUEPRINT.route("/post_imgs", methods=["POST", "OPTIONS"])
def post_images():
    request_start = time.time()
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
    elif request.method == "POST": # The actual request following the preflight
        imgs_list = request.files.getlist("imgs[]")
        # names = [f.filename for f in imgs_list]
        print(imgs_list)
        try:
            result = get_distances(imgs_list)
            log_results(result, request, request_start)
        except Exception as e:
            # print("Error:")
            print(" ** Exception: {}".format(str(e)))
            log_error(request, request_start, e)
            # TODO: return dict of {"error": str(e)}
            return _corsify_actual_response({"error": str(e)}, 400)
        output = {"resultsArray": result}
        return _corsify_actual_response(output)
    else:
        raise RuntimeError("Weird - don't know how to handle method {}".format(request.method))

def get_request_ip(request):
    return request.headers.get('x-forwarded-for', request.remote_addr)

def _build_cors_preflight_response():
    """Handles preflight response (OPTIONS)"""
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def _corsify_actual_response(output, code=None):
    response = jsonify(output)
    response.headers.add("Access-Control-Allow-Origin", "*")
    if code: # Defaults to 200
        response.status_code = code
    return response

def get_distances(img_list):
    """
    Return a list of tuples [(img1, img2, norm_1_2),..]
    Currently only handles the first 2 or 3 images in a list.
    """
    if not len(img_list) >= 2:
        raise Exception("must compare 2 or more images")
    img1 = img_list[0]
    img2 = img_list[1]
    rep1 = getRep(img1)
    rep2 = getRep(img2)
    d = rep1 - rep2
    norm_12 = norm(d)
    file1 = img1.filename
    file2 = img2.filename
    print("==Norm: " + norm(d) + ",{},{}".format(file1,file2))
    result = [(file1, file2, norm_12)]
    if len(img_list) == 3:
        img3 = img_list[2]
        rep3 = getRep(img3)
        d_13 = rep1 - rep3
        d_23 = rep2 - rep3
        file3 = img3.filename
        result.append((file1, file3, norm(d_13)))
        result.append((file2, file3, norm(d_23)))
        print("==Norm 2: " + str(result[1]))
        print("==Norm 3: " + str(result[2]))
    return result

LOG_FILE = "kevin_openface_log.txt"

def log_results(result, request, start_time):
    logfile = open(LOG_FILE, "a")  # append mode
    ip_string = get_request_ip(request)
    iso_time = time.strftime('%Y-%m-%d %H:%M:%S %Z',time.gmtime(start_time))
    time_elapsed = "{:.3f}".format(time.time() - start_time)
    # Output: Timestamp, time to result computed, IP, Image 1, Image 2, Norm
    # or a longer result if comparing 3 files
    tup_string = ""
    for tup in result:
        tup_string += "{},{},{}".format(*tup)
    logfile.write(",".join([iso_time, time_elapsed, ip_string, tup_string]) + "\n")
    logfile.close()
    return result

def log_error(request, start_time, exc):
    logfile = open(LOG_FILE, "a")  # append mode 
    ip_string = get_request_ip(request)
    iso_time = time.strftime('%Y-%m-%d %H:%M:%S %Z',time.gmtime(start_time))
    time_elapsed = "{:.3f}".format(time.time() - start_time)
    # Output: Timestamp, time to result computed, IP, Image 1, Image 2, Norm
    # or a longer result if comparing 3 files
    # tup_string = ""
    # for tup in result:
    #     tup_string += "{},{},{}".format(*tup)
    logfile.write(",".join([iso_time, time_elapsed, ip_string, "Exception: " + str(exc)]) + "\n")
    logfile.close()

def norm(array):
    """Norm of array formatted to 3 digits"""
    return "{:0.3f}".format(np.dot(array, array))

