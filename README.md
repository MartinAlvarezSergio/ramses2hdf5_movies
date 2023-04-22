# ramses2hdf5_movies
11;rgb:1e1e/1e1e/1e1e11;rgb:1e1e/1e1e/1e1e
This code compiles RAMSES standard movie files in format ".map" into a single HDF5 file.
In its current state, it only combines a single movie snapshot into each file. 

This is intended to reduce the number of inodes used by the RAMSES movie files + facilitate
transfer across HPC facilities. As a side advantage, it also provides faster access when reading
multiple movie files.

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Installation 

While the python code requires no installations, I have included a short python executable compiler to allow use without invoking python.

## Usage

Please review the code internal configuration prior to your first execution to make sure no major RAMSES changes affect the usability of this code. You can find this at the top of combine_movies.py

While the code executes automatically, there's a number of useful options you should take a look to before you execute:
--iniID    : (Int) First movie ID to be converted (default=1)
--finID    : (Int) Last movie ID to be converted (default=5000)
--path     : (String) Path to the simulation directory containing the movie folders (default='./')
--clean    : DO Clean .map files after succesfully converted to HDF5 (default=False)
--no_clean : DO NOT clean .map files after succesfully converted to HDF5 (default=False)
--safe     : DO skip the last found .map set of files to ensure no empty files are used (default=True)
--no_safe  : DO NOT skip the last found .map set of files. Warning: may interfere with ongoing sims (default=True)

If you want to execute this on your simulation, simply provide a path to the simulation folder containing all your 'movie' folders:
$ python combine_movies.py --iniID 1 --finID 5000 --no_clean --safe --path /path/to/simulation/folder/ 

This command will convert all the movie files in that simulation to HDF5 format, dumped in a new folder at the provided path named "HDF5movies". The default "no_clean" configuration will preserve the old movie files. I recommend that prior to executing with the --clean option, you ensure that you can access the HDF5 files and that they work.

To do this, and to access the maps inside the generated hdf5 files, you can use the python routines provided inside the utils folder. You can execute the standalone io_hdf5.py code which contains a rapid example of a gas density movie map:
$ python io_hdf5.py --path /path/to/allmoviesHDF5/file

Only once you have done the following, I recommend using the --clean option:
- Reviewed the general configuration inside combine_movies.py
- Converted a few movie files and ensure that the code works appropriately for your simulation
- Reviewed the data inside the HDF5 files

In addition, the code executes by default with the --safe option. If this is activated, the last movie snapshot found for your simulation is not processes. This is to avoid the possibility of interacting with ongoing simulation map dumps.

## Licence

This project is licensed under the MIT License - see the LICENSE.md file for details
