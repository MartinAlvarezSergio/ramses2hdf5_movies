import numpy as np

######################################################################################
# This function reads the full information from a RAMSES infofile
def read_infofile_full(infopath):
    # Open infofile and read all data up until the ordering type.
    # In this version, ordering type and domain indices are ignored
    with open(infopath, "r") as infofile:
        linehead = "empty"
        integ_type = True
        infofile_data = dict()
        while linehead != "unit_t":
            newline = infofile.readline()
            linehead = newline[0:12].strip()
            if len(linehead) == 0:
                continue  # Skip empty lines
            if integ_type == True:
                newdata = int(newline[13:].strip())
            if integ_type == False:
                newdata = float(newline[13:].strip())
            infofile_data[linehead] = newdata
            if linehead == "nstep_coarse":
                integ_type = False
    # Compute corresponding redshift
    infofile_data["zeta"] = 1.0 / infofile_data["aexp"] - 1.0
    # Compute maximum resolution
    infofile_data["dres"] = 1.0 / (2 ** infofile_data["levelmax"])
    # Compute unit mass (code to solar masses)
    mfac = (infofile_data["unit_d"] * infofile_data["unit_l"]) * infofile_data[
        "unit_l"
    ] ** 2
    g2msun = 5.0e-34
    infofile_data["unit_m"] = mfac * g2msun
    # Return infofile_data without any further operations
    return infofile_data

######################################################################################
# This function reads the full information from a RAMSES infofile
def read_rt_infofile_full(rt_infopath, lactive):
    # Open infofile and read all data up until the ordering type.
    # In this version, ordering type and domain indices are ignored
    with open(rt_infopath, "r") as rt_infofile:
        linehead = "empty"
        integ_type = True
        rt_infofile_data = dict()
        # Read first part of header
        while linehead != "unit_pf":
            newline = rt_infofile.readline()
            linehead = newline[0:12].strip()
            if len(linehead) == 0:
                continue  # Skip empty lines
            if integ_type == True:
                newdata = int(newline[13:].strip())
            if integ_type == False:
                newdata = float(newline[13:].strip())
            rt_infofile_data[linehead] = newdata
            if linehead == "rtprecision":
                integ_type = False
        # Read reduced speed of light information
        newline = rt_infofile.readline()
        linehead = newline[0:11].strip()
        newdata = np.array(newline[13:].split()).astype(np.float)
        rt_infofile_data[linehead] = newdata
        # Read star formation data
        while linehead != "g_star":
            newline = rt_infofile.readline()
            linehead = newline[0:11].strip()
            if len(linehead) == 0:
                continue  # Skip empty lines
            newdata = float(newline[13:].strip())
            rt_infofile_data[linehead] = newdata
        # Read photon group properties header
        while linehead != "spec2group":
            newline = rt_infofile.readline()
            if len(newline) > 16:
                if newline[16] != "=":
                    continue  # Skip non-data lines
            else:
                continue
            linehead = newline[0:16].strip()
            if len(linehead) == 0:
                continue  # Skip empty lines
            linehead = linehead.replace("[eV]", "").strip()
            newdata = np.array(newline[17:].split()).astype(np.float)
            rt_infofile_data[linehead] = newdata
        # Read photon group properties header
        igroup = -1
        ngroups = rt_infofile_data["nGroups"]
        while (linehead != "cse" + str(ngroups)) or (igroup < ngroups):
            newline = rt_infofile.readline()
            if len(newline) > 16:
                if newline[16] != "=":
                    continue
            elif len(newline) > 11:
                if newline[2:10] == "---Group":
                    igroup = int(newline[10:12])
                    continue
                else:
                    continue  # Skip non-data lines with no group information
            else:
                continue
            linehead = newline[0:16].strip()
            if len(linehead) == 0:
                continue  # Skip empty lines
            linehead = linehead.replace("[eV]", "").strip()
            linehead = linehead.replace("[cm^2]", "").strip()
            linehead = linehead + str(igroup)
            newdata = np.array(newline[17:].split()).astype(np.float)
            rt_infofile_data[linehead] = newdata
    # Return rt_infofile_data without any further operations
    return rt_infofile_data

######################################################################################
# This function reads a map from a data file
def readmap_from_file(mappath, do_debug=False):
    with open(mappath, "r") as mapfile:
        map_header = dict()
        aexp, dx, dy, dz = read_fortran_num_uf(mapfile, 4, np.float64)
        map_header["aexp"] = aexp
        map_header["dx"] = dx
        map_header["dy"] = dy
        map_header["dz"] = dz
        nx, ny = read_fortran_num_uf(mapfile, 2, np.int32)
        map_header["nx"] = nx
        map_header["ny"] = ny
        map_header["nz"] = 1
        map_header["dxres"] = map_header["dx"] / map_header["nx"]
        map_header["dyres"] = map_header["dy"] / map_header["ny"]
        map_header["dres"] = max(map_header["dxres"], map_header["dyres"])

        pf = read_fortran_matrix_uf(mapfile, (nx, ny), np.float32)
        # data=read_fortran_num_uf(mapfile,nx*ny,np.float32)
        # pf=np.array(data).reshape((nx,ny),order='F')
        pf = np.rot90(pf, k=-1)
        # pf=np.array(data).reshape((nx,ny))

    if do_debug:
        print("Map read from mappath:")
        print("min=", pf.min(), "max=", pf.max())

    return pf, map_header


######################################################################################

# Reads a set of numbers from a fortran binary
def read_fortran_num_uf(fin,nelements,rtype):
    ignore = np.fromfile(file=fin, dtype=np.int32, count=1)
    read_numbers=np.fromfile(file=fin, dtype=rtype, count=nelements)
    ignore = np.fromfile(file=fin, dtype=np.int32, count=1)
    if (nelements==1): return read_numbers[0]
    return read_numbers[0:nelements+1]
# Reads a set of numbers from a fortran binary
def read_fortran_matrix_uf(fin,dims,rtype):
    nelements=np.prod(dims)
    ignore = np.fromfile(file=fin, dtype=np.int32, count=1)
    read_matrix=np.fromfile(fin,dtype=rtype, count=nelements).reshape(dims,order='F')
    ignore = np.fromfile(file=fin, dtype=np.int32, count=1)
    return read_matrix