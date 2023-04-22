import os

# from icecream import ic

from io_functions import read_infofile_full, read_rt_infofile_full, readmap_from_file, read_fortran_num_uf
class MovieData:
    def __init__(self,req_movie_names=[]):
        # Configuration initialisation
        self.quiet=False
        self.verbose=False
        if (self.quiet): self.verbose=False

        # Identity initialisation
        self.myid=1
        self.me="MD"+str(self.myid)+": "

        # Movie types
        self.movlist=True
        self.movie_names=["dm","dens","stars","temp","pmag","pcrs","xHII","xHeII","xHeIII","lum","var"]
        if (isinstance(req_movie_names,list)):
            if (len(req_movie_names)>0):
                self.movie_names=req_movie_names
            if ("var" in self.movie_names):
                self.movie_names.remove('var')
                for ii in range(0,99):
                    self.movie_names.append("var"+str(ii))
        else:
            if (req_movie_names in ["all","All"]):
                self.movlist=False
            else:
                raise Exception ("Error: unrecognised req_movie_names")
                    

        # Infofile initialisation
        self.infofile_data=0
        self.from_movie=0
        self.rt_infofile_data=0

        # Read files data
        self.read_files=[]
        self.movies_header=dict()
        self.movies_data=dict()
        
        
        # Initialisation completed
        if (self.verbose):
            self.pinf=self.me
        else:
            self.pinf=""
        return
    def read_infofile(self,movie_folder,IDname):
        infofile_read=False
        infofile_path=movie_folder+"/info_"+IDname+".txt"
        if (os.path.isfile(infofile_path)==False):
            print(self.pinf+"Movies not found for output "+IDname+" in "+movie_folder)
            return infofile_read
        if (self.infofile_data==0):
            self.infofile_data=read_infofile_full(infofile_path)
            self.from_movie=movie_folder
            infofile_read=True
        else:
            new_infofile_data=read_infofile_full(infofile_path)
            compatible=True
            for idata in new_infofile_data:
                if (new_infofile_data[idata] != self.infofile_data[idata]):
                    compatible=False
                    print(self.pinf+"New infofile ("+IDname+") incompatible with internal data")
                    print(self.pinf+"Internal "+idata+"="+str(self.infofile_data[idata]))
                    print(self.pinf+"External "+idata+"="+str(new_infofile_data[idata]))
                    os.stop()                    
            if (compatible):
                if(self.verbose): print(self.pinf+"New infofile (ID="+IDname+") from "+movie_folder+" is compatible with internal data from "+self.from_movie)
                infofile_read=True
        if (infofile_read): self.read_files.append(infofile_path)
        return infofile_read
    def read_rt_infofile(self,movie_folder,IDname):
        rt_infofile_path=movie_folder+"/rt_info_"+IDname+".txt"
        lactive=self.infofile_data["levelmax"]-self.infofile_data["levelmin"]+1
        if (self.rt_infofile_data==0):
            self.rt_infofile_data=read_rt_infofile_full(rt_infofile_path,lactive)
        else:
            new_rt_infofile_data=read_rt_infofile_full(rt_infofile_path,lactive)
            compatible=True
            for idata in new_rt_infofile_data:
                if (new_rt_infofile_data[idata] != self.rt_infofile_data[idata]):
                    compatible=False
                    print(self.pinf+"New rt_infofile ("+IDname+") incompatible with internal data")
                    print(self.pinf+"Internal "+idata+"="+str(self.rt_infofile_data[idata]))
                    print(self.pinf+"External "+idata+"="+str(new_rt_infofile_data[idata]))
                    os.stop()                    
            if (compatible): print(self.pinf+"New rt_infofile (ID="+IDname+") is compatible with internal data")
        self.read_files.append(rt_infofile_path)
        return
    def read_allmovie_files(self,movie_folder,movID,IDname):
        all_data=dict()
        map_header=None
        print(self.pinf+"Reading maps from:\n"+movie_folder+" (ID="+IDname+")")
        print(self.pinf+"Variables read",end=": ")
        prec=""
        # Read each recognised map
        read_files={}
        if (self.movlist):
            for new_name in self.movie_names:
                path2moviefile=movie_folder+"/"+new_name+"_"+IDname+".map"
                if (os.path.isfile(path2moviefile)):
                    read_files[new_name]=path2moviefile
        else:
            file_list = os.listdir(movie_folder)
            remmatch="_"+IDname+".map"
            for new_name in file_list:
                if (new_name.endswith('.map') and (IDname in new_name)):
                    path2moviefile=movie_folder+"/"+new_name
                    use_name=new_name.replace(remmatch,"",-1)
                    read_files[use_name]=path2moviefile
        for new_name, path2moviefile in read_files.items():
            print(prec+new_name, end="")
            prec=", "
            pf, new_map_header=readmap_from_file(path2moviefile)
            # Save new map header or check whether it is consistent with internal
            if (map_header==None): map_header=new_map_header                    
            for idata in new_map_header:
                if (new_map_header[idata] != map_header[idata]):
                    print("Found incompatible map_header, stopping")
                    os.stop()                    
            self.read_files.append(path2moviefile)
            all_data[new_name]=pf
        print()
        self.movies_header[movID]=map_header
        self.movies_data[movID]=all_data
        return
    def insert2hdf5file(self,hf,g,IDname):
        check_writing=False
        print(self.pinf+"Writing all movies for ID="+IDname+" to hdf5 file...")
        # Create a new group for the read output    
        goutput=g.create_group(IDname)
        # Dump all the infofile information into the output group
        for infoline in self.infofile_data:
            if (check_writing): print("Writing attrib="+infoline+", data="+str(self.infofile_data[infoline]))
            goutput.attrs[infoline]=self.infofile_data[infoline]
        if (self.rt_infofile_data!=0):
            for rt_infoline in self.rt_infofile_data:
                if (check_writing): print("Writing attrib="+rt_infoline+", data="+str(self.rt_infofile_data[rt_infoline]))
                goutput.attrs[rt_infoline]=self.rt_infofile_data[rt_infoline]
        # Now write all the movies data into the infofile
        for movie_folder in self.movies_data:            
            # Create new group for each movie folder
            gmovie=goutput.create_group(movie_folder)
            # Dump all the map_header information into the movie folder group
            movie_header=self.movies_header[movie_folder]
            for mapheaderline in movie_header:
                if (check_writing): print("Writing attrib="+mapheaderline+", data="+str(movie_header[mapheaderline]))
                gmovie.attrs[mapheaderline]=movie_header[mapheaderline]
            # Now write all the movies data to file
            all_data=self.movies_data[movie_folder]
            for data in all_data:                
                if (check_writing): print("Writing data for "+data)
                din=gmovie.create_dataset(data, data=all_data[data])
        # Writing completed, return
        return
