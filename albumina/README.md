
## Get the Source Structures

```bash
mkdir -p source
cd source

# Fetch the albumina PDB http://doi.org/10.1080/19420862.2016.1185581
wget https://files.rcsb.org/download/5FUO.pdb

# Fetch the amyloid 42 - alpha PDB https://doi.org/10.1046/j.1432-1033.2002.03271.x
wget https://files.rcsb.org/download/1IYT.pdb

# Fetch the amyloid 42 - beta PDB http://doi.org/10.1126/science.aao2825
wget https://files.rcsb.org/download/5OQV.pdb

cd ..
```

## Individualize Regions of Interest

```bash
mkdir -p segments
cd segments
```

We will use *PyMol* for the selection of the key segments.
The albumin_cterm will always be assigned as *chain A* while any putative binder
will be assigned as *chain B*.

Following are the *PyMol* commands:
```bash
load ../source/1IYT.pdb
load ../source/5FUO.pdb
load ../source/5OQV.pdb
alter 1IYT, chain='B'
save amyloid_alpha.pdb, 1IYT, state=1
save albumin_cterm.pdb, 5FUO and i. 504-538
alter 5FUO, chain='B'
save albumin_cterm_lid.pdb, 5FUO and i. 539-582
save amyloid_beta.pdb, 5OQV and c. B
```

### Creating the model for clusterin

```bash
mkdir -p model
cd model
```

We will run **MODELLER** following the alignment in ```clusterin.pir```, based in the structure of the ```albumin_cterm``` region by
using the ```simpleModel.py``` script, obtaining 5 alternative models.

Then the models will be minimized and repacked with the ```min_pack_min``` Rosetta application.

```bash
~/local/repos/rosetta/main/source/bin/min_pack_min.linuxgccrelease -in:file:s clusterin.B*pdb -out:file:silent clusterin.models.minimized.silent
```

As the structure clusterin.B99990004_0001.pdb scores far better than the rest according to Rosetta (```-23.079``` while the second performer scores ```-12.829```),
we select that one as the segment to use in the following steps.

```bash
cp clusterin.B99990004_0001.pdb ../clusterin.pdb
cd ../..
```

## Preparing Docking

```bash
mkdir -p docking/{clust_alpha,clust_beta,amyloid_alpha,amyloid_beta,albumin_cterm_lid}
```

The input for docking with Rosetta is a file containing the two structures placed a no more than
10A from each other. The preparation of these files will be done by hand in *PyMol* and placed into
their respective folders.

## Docking

*Actual execution was performed on cluster, thus naming of the decoys include JOBID and ARRAYID*

```bash
cd docking/clust_alpha
$ROSETTABIN/rosetta_scripts.linuxiccrelease -parser:protocol ../docking.xml -s clust_alpha.pdb -ex1 -ex2 -docking:sc_min -randomize2 -randomize1 -nstruct 10000 -out:file:silent clust_alpha.silent
minisilent.py -in:file clust_alpha.silent -out:file clust_alpha.minisilent.gz
cd ../clust_beta
$ROSETTABIN/rosetta_scripts.linuxiccrelease -parser:protocol ../docking.xml -s clust_beta.pdb -ex1 -ex2 -docking:sc_min -randomize2 -randomize1 -nstruct 10000 -out:file:silent clust_beta.silent
minisilent.py -in:file clust_beta.silent -out:file clust_beta.minisilent.gz
cd ../amyloid_alpha
$ROSETTABIN/rosetta_scripts.linuxiccrelease -parser:protocol ../docking.xml -s alpha.pdb -ex1 -ex2 -docking:sc_min -randomize2 -randomize1 -nstruct 10000 -out:file:silent alpha_dock.silent
minisilent.py -in:file alpha_dock.silent -out:file alpha_dock.minisilent.gz
cd ../amyloid_beta
$ROSETTABIN/rosetta_scripts.linuxiccrelease -parser:protocol ../docking.xml -s beta.pdb -ex1 -ex2 -docking:sc_min -randomize2 -randomize1 -nstruct 10000 -out:file:silent beta_dock.silent
minisilent.py -in:file beta_dock.silent -out:file beta_dock.minisilent.gz
cd ../albumin_cterm_lid
$ROSETTABIN/rosetta_scripts.linuxiccrelease -parser:protocol ../docking.xml -s lid.pdb -ex1 -ex2 -docking:sc_min -randomize2 -randomize1 -nstruct 10000 -out:file:silent lid_dock.silent
minisilent.py -in:file lid_dock.silent -out:file lid_dock.minisilent.gz
cd ../..
```

## Analysis

Analysis of the generated decoys is performed in the attached *jupyter notebook*.
