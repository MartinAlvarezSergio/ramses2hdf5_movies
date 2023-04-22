import os
import argparse
# from icecream import ic
from misc_functions import read_name_funct

# from misc_functions import *

####################################################
def find_movie_files(movie_folders, iniID, finID, movie_path, imov_min=1, imov_max=9):
    exist_movies = {}
    rt_infofiles = False
    # Check whether movie folders exist
    for movie in movie_folders:
        for iim in range(imov_min, imov_max + 1):
            movID = movie + str(iim)
            movreq = movie_path + movID
            exist_movies[movreq] = {"found": os.path.isdir(movreq), "mov": movID}
    # Check whether movie files exist, and determine min-max range of movies
    IDmin = finID
    IDmax = iniID
    for movie_folder, movprops in exist_movies.items():
        exists=movprops["found"]
        if not exists:
            continue
        file_list = os.listdir(movie_folder)
        found_movies = False
        for imovie in range(iniID, finID + 1):
            IDname = read_name_funct(imovie)
            if os.path.isfile(movie_folder + "/info_" + IDname + ".txt"):
                # Look for map files
                map_files_exist = any(
                    f.endswith(".map") and (IDname in f) for f in file_list
                )
                if not map_files_exist:
                    print(
                        "Warning! Info files found for", IDname, "but no matching maps!"
                    )
                IDmin = min(imovie, IDmin)
                IDmax = max(imovie, IDmax)
                found_movies = True
            if os.path.isfile(movie_folder + "/rt_info_" + IDname + ".txt"):
                rt_infofiles = True
        if found_movies == False:
            exists = False
    print("Found movies for:")
    for movname, movprops in exist_movies.items():
        movfound = movprops["found"]
        if movfound:
            print(movname)
    return exist_movies, IDmin, IDmax, rt_infofiles


####################################################
def read_system_arguments(arguments):
    warn_frame = "Warning: you have deactivated the protection cut that leaves the last frame found untouched"
    warn_clean = "Warning: you have activated the removal of .map files after their conversion to HDF5"
    parser = argparse.ArgumentParser(description="TODO")
    parser.add_argument(
        "-ini",
        "--iniID",
        type=int,
        default=1,
        help="(Int) First movie ID to be converted (default=1)",
    )
    parser.add_argument(
        "-fin",
        "--finID",
        type=int,
        default=5000,
        help="(Int) Last movie ID to be converted (default=5000)",
    )
    parser.add_argument(
        "-pth",
        "--path",
        type=str,
        default=".",
        help="(String) Path to the simulation directory containing the movie folders (default='./')",
    )
    parser.add_argument(
        "-cln",
        "--clean",
        dest="clean",
        action="store_true",
        default=False,
        help="DO Clean .map files after succesfully converted to HDF5 (default=False)",
    )
    parser.add_argument(
        "-noc",
        "--no_clean",
        dest="clean",
        action="store_false",
        default=False,
        help="DO NOT clean .map files after succesfully converted to HDF5 (default=False)",
    )
    parser.add_argument(
        "-sfe",
        "--safe",
        dest="safe",
        action="store_true",
        default=True,
        help="DO skip the last found .map set of files to ensure no empty files are used (default=True)",
    )
    parser.add_argument(
        "-nos",
        "--no_safe",
        dest="safe",
        action="store_false",
        default=True,
        help="DO NOT skip the last found .map set of files. Warning: may interfere with ongoing sims (default=True)",
    )
    args = parser.parse_args()
    # Final warnings and modifications to received arguments
    if args.clean:
        print(warn_clean)
    if not args.safe:
        print(warn_frame)
    args.path = args.path + "/"
    return args


####################################################
# Useful default initialisations and others
help_text = "Required parameters are:\n    [1] initial movie ID to be requested\n    [2] final movie ID to be requested\n    [3] cleaning flag. Activate by providing 'clean'\n"
end_text = "combine_movies.py completed execution successfully :)"
####################################################
