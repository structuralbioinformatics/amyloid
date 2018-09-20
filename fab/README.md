
## Search IG structures

Search will be performed through the **PDB API**, the search will be based on the following parameters:

* Human proteins
* With a resolution under 2.5A
* With the **IMMUNOGLOBULIN** keyword.

Search is executed with `search/pdbsearch.py`, which also performs homology filtering.

From the search two non-homologous structures arose: **8FAB** and **2F5B**.

## Docking

Docking was performed with **PatchDock** and scored with **Rosetta**. All combinations of dockings are stores in `dock`.
