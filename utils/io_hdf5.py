######################################################################################
# This function reads all the infofile (and rt_infofile if available) data
def read_infofile_from_hdf5(hf, IDname):
    output_data = hf["all_outputs"][IDname]
    infofile_data = dict()
    for attr in output_data.attrs.keys():
        infofile_data[attr] = output_data.attrs[attr]
    return infofile_data

######################################################################################
# This function reads a map from an HDF5 file
def readmap_from_hdf5(hf, movie_folder, IDname, varname):
    output_data = hf["all_outputs"][IDname][movie_folder]
    # Generate map header
    map_header = dict()
    for attr in output_data.attrs.keys():
        map_header[attr] = output_data.attrs[attr]
    # Returns the map data if map exists within output_data. Otherwise return empty map
    if varname in output_data:
        map_data = output_data[varname].value
    else:

        map_data = np.zeros([int(map_header["nx"]), int(map_header["ny"])])
    return map_data, map_header

######################################################################################

######################################################################################
######################################################################################
######################################################################################
######################################################################################
def main():
    import argparse
    import h5py
    import re
    from icecream import ic
    # Read required help from screen
    print("\n:> io_hdf5.py isolated execution\n")
    parser = argparse.ArgumentParser()
    parser.add_argument("--path",type=str,help="(String) Path to HDF5 file")
    args=parser.parse_args()
    hf = h5py.File(args.path,'r')
    pattern = r"_([^_]+)\.h5$"
    IDname= re.search(pattern, args.path).group(1)
    req_movie="movie1"
    infofile_data = read_infofile_from_hdf5(hf,IDname)
    ic(infofile_data)
    pf, map_header=readmap_from_hdf5(hf,req_movie,IDname,"dens")
    ic(map_header)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm
    plt.imshow(pf, norm=LogNorm())
    plt.savefig("example_map"+IDname+".png")
    return


if __name__ == "__main__":
    main()