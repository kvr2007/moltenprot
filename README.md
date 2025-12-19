# MoltenProt
![screenshot of main window](moltenprot/doc/MainWindow.png)

MoltenProt is a graphical and command-line application for fitting protein thermal unfolding data. For more details see the publication:

**In-depth interrogation of protein thermal unfolding data with MoltenProt**

[https://doi.org/10.1002/pro.3986](https://doi.org/10.1002/pro.3986)

## Installation

If you have python (versions 3.8-3.10) available on your system, you can install MoltenProt as follows: 

1. (OPTIONAL) create a virtual environment:
    
    `python -m venv venv`
    
2. (OPTIONAL) activate a virtual environment:

    a. Windows:
    
        `venv\Scripts\activate`
        
    b. GNU/Linux and Mac:
    
        `source venv/bin/activate`

3. Install the MoltenProt package from this repo:
    
    `pip install git+https://github.com/kvr2007/moltenprot.git@master#egg=moltenprot[gui,multiproc]`
    
    (this will install with GUI and multiprocessing capability)

You can now launch the GUI with command `moltenprot_gui` or access the CLI with `moltenprot`.

For additional documentation see [INSTALL](INSTALL).

[CHANGELOG](CHANGELOG)

### Pre-packaged binaries

Older versions of MoltenProt packaged for Mac and Windows are available here:

http://marlovitslab.org/lab/Download.html

## Usage

User guide is available in [PDF format](moltenprot/doc/index.pdf) and also from the GUI "Help > MoltenProt help".

## Getting help

Please open an issue [here](https://github.com/kvr2007/moltenprot/issues).
