import argparse
import subprocess
from string import Template


parser = argparse.ArgumentParser(description="Process a pdb file for dynamics simulation in a water box")

parser.add_argument("--baseName", help="the base name for the files, generally the PDB-ID")
parser.add_argument("--solPadding", help="Padding of the water box, in angstroms, defalut 15")
parser.add_argument("--saltConc", help="the concentration (in M) of salt for adding ions after equlibrating charge. default 0.15 M")

args = parser.parse_args()

if args.baseName:
    basen = args.baseName
else:
    basen = "protein"

if args.solPadding:
    pad = args.solPadding
else:
    pad = 15

if args.saltConc:
    conc = args.saltConc
else:
    conc = "0.15"


    
VMD_TEMPLATE="""### VMD process script

### Generate the psf file
package require psfgen
psfgen_logfile "load_topology.log"
topology top_all36_prot.rtf
psfgen_logfile close

psfgen_logfile "structure_prep.log"

pdbalias residue HIS HSE
pdbalias atom ILE CD1 CD

segment P {{pdb {name}.pdb}}

coordpdb {name}.pdb P

guesscoord

writepdb {name}.processed.pdb

writepsf {name}.processed.psf

### Solvate the protein in a water box with {pad}  angstrom padding
package require solvate
solvate {name}.processed.psf {name}.processed.pdb -t {pad} -o {name}.wb

### Neutralize the system charge and set the concentration of NaCl to 150 mM

package require autoionize
autoionize -psf {name}.wb.psf -pdb {name}.wb.pdb -sc {conc} -o {name}.wb.ions

### Load the system
resetpsf
mol load psf {name}.wb.ions.psf pdb {name}.wb.ions.pdb

### Center the system around the origin for simplicity
### Make this the last step before generatine the NAMD conf file (VIGNESH will evaluate this)

set sel [atomselect top "all"]
set cen [measure center $sel]
set m1 [trans origin $cen]

$sel move $m1

$sel writepsf {name}.final.psf
$sel writepdb {name}.final.pdb


exit 

"""

print(VMD_TEMPLATE.format(name=basen, pad=pad, conc=conc))
