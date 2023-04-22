##############################################################################
# combine_movies.py
# This python script compiles all the RAMSES standard format movies produced
# for a movie snapshot (i.e. 00000) within a simulation and combines them in
# a single hdf5 file. It currently generates one new file per snapshot to
# reduce the use of inodes per movie output and provide faster access when
# generating movie maps using MPI multi-file access.
# Generating movies read from HDF5 compared with the classical method
# employing 12 MPI processes yielded the following times:
# t_classic = 1864 +- 61
# t_HDF5    = 1447 +- 76
# This leads to a reduction of about 20% cost computation time.
# Nonetheless, converting the movies to HDF5 is a fairly slow computation.
#
# Created (05/05/2021): S. Martin-Alvarez 
# Updated (21/04/2023): general polish + added remote execution
##############################################################################
import h5py
import sys
import os
# from icecream import ic

from movie_data import MovieData
from misc_functions import print_header
from combine_movies_functions import *

####################################################
# Internal configuration - PLEASE REVIEW THIS BEFORE YOUR FIRST EXECUTION!
movie_folders=["movie"] # Names of movie folders that can contain the required .map files
other_config={}
other_config["imov_min"]=1 # Minimum number of movie folders to be checked (e.g. "movie1/") 
other_config["imov_max"]=9 # Maximum number of movie folders to be checked (e.g. "movie9/")
hdf5folder="HDF5movies" # Results folder onto which the HDF5 movies will be written
# The following list contains the names of all movie names to be processed into the HDF5 file
# If you add "var" to the list, it will process all "varXX" movies with XX between 0 and 30 (see movie_data.py)
# Alternatively, you can request req_movie_names="all", and all ".map" files will be included
req_movie_names=["dm","dens","stars","temp","pmag","pcrs","xHII","xHeII","xHeIII","lum","var"]
req_movie_names="all"
####################################################

# Read user provided data ###############################################################################
print_header("combine_movies",mode="default")
args=read_system_arguments(sys.argv)
hdf5folder=args.path+hdf5folder
# Check whether any movies exist and save min-max output IDs (within range provided above) ##############
exist_movies,IDmin,IDmax,rt_infofiles=find_movie_files(movie_folders,args.iniID,args.finID,args.path,**other_config)
# If movies are found, create new directory for HDF5 to be placed into ##################################
if (os.path.isdir(hdf5folder)==False): os.mkdir(hdf5folder)
# Skip the latest movie output to avoid interacting with a simulation that is currently writing
# its movie files 
if (args.safe):
    IDmax=IDmax-1
    print("Note: currently reducing IDmax by 1 to avoid interferring with ongoing simulations ")
# Loop over all movie output IDs
print("Converting movies with IDs between "+str(IDmin)+" and "+str(IDmax)+"...")
for imovie in range(IDmin,IDmax+1):    
    # Create new movie generator for current output
    IDname=read_name_funct(imovie)
    movie_compilation=MovieData(req_movie_names=req_movie_names)
    # Read movies from all movie folders
    print("############## Compiling movies for ID="+IDname)
    for ifolder, (req_folder, movprops) in enumerate(exist_movies.items()):
        exists=movprops["found"]
        movID=movprops["mov"]
        if (not exists): continue
        file_read=movie_compilation.read_infofile(req_folder,IDname)
        if (not file_read): continue
        if (rt_infofiles and ifolder==0): movie_compilation.read_rt_infofile(req_folder,IDname)
        movie_compilation.read_allmovie_files(req_folder,movID,IDname)
    ### Write new HDF5 file and cleaning if required
    ftext="Now commencing file output and cleaning, please do not interrupt"
    if (len(movie_compilation.read_files)>0): print(ftext)        
    ### Dump all the information into a new HDF5
    if (len(movie_compilation.read_files)>0):
        hdf5name="allmovies"
        hdf5file=hdf5folder+"/"+hdf5name+"_"+IDname+".h5"
        print("HDF5 file is: "+hdf5file)
        hf=h5py.File(hdf5file,'w')
        group=hf.create_group('all_outputs')
        movie_compilation.insert2hdf5file(hf,group,IDname)
        hf.close()
    ### If cleaning is active, delete movie files
    if (len(movie_compilation.read_files)>0):
        announce_clean=False
        if (args.clean):
            if (announce_clean):
                print("Cleaning movie files:")
                print(movie_compilation.read_files)
            for readfile in movie_compilation.read_files:
                rm_command="rm "+ readfile
                os.system(rm_command)
        else:
            if (announce_clean):
                print("Cleaning is not activated. I would be deleting:")
                for readfile in movie_compilation.read_files:
                    print(readfile)
# Close code
print(end_text)
print()
