
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

```bash
cd ..
```

## Preparing Docking

```bash
mkdir -p docking/{amyloid_alpha,amyloid_beta,albumin_cterm_lid}
```

The input for docking with Rosetta is a file containing the two structures placed a no more than
10A from each other. The preparation of these files will be done by hand in *PyMol* and placed into
their respective folders.

## Docking

```bash
cd docking/amyloid_alpha

cd ..
```
