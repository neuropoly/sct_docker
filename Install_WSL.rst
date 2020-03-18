.. -*- coding: utf-8; indent-tabs-mode:nil; -*-

############################################################
Spinal Cord Toolbox for Windows : Windows subsystem for linux
############################################################

This documentation shows how to install the latest version of SCT. If you want to install a different version of SCT please specify the version number.

.. contents::
..
    1  Windows subsystem for linux 
    2  environment preparation
    3  SCT installation 
    4  FSL installation 
    5  Usage 

Installation
************


#. Install `Xming <https://sourceforge.net/projects/xming/>`_.

#. Install  `Windows subsystem for linux and initialize it <https://docs.microsoft.com/en-us/windows/wsl/install-win10>`_. 

	- Please install the Ubuntu 18.04 LTS distro. 

Environment preparation
***********************

Run the following command to install various packages that will be needed to install FSL and SCT. This will require your password

.. code-block:: sh

    sudo apt-get -y update
    sudo apt-get -y install gcc
    sudo apt-get -y install unzip
    sudo apt-get install -y python-pip python
    sudo apt-get install -y psmisc net-tools
    sudo apt-get install -y git
    sudo apt-get install -y gfortran
    sudo apt-get install -y libjpeg-dev
    echo 'export DISPLAY=127.0.0.1:0.0' >> .profile


Install SCT
*********** 

Download SCT:

.. code-block:: sh

  git clone https://github.com/neuropoly/spinalcordtoolbox.git sct
  cd sct

To select a [specific release](https://github.com/neuropoly/spinalcordtoolbox/releases), replace X.Y.Z below with the proper release number. If you prefer to use the development version, you can skip this step.

.. code-block:: sh

  git checkout X.Y.Z

Install SCT:

.. code:: sh
 
    yes | ./install_sct



Install FSL
***********

FSL contains fsleyes which is the default viewer for NIfTI image in SCT. 
Download and execute the installer:
 
.. code-block:: sh

    wget https://fsl.fmrib.ox.ac.uk/fsldownloads/fslinstaller.py
    python fslinstaller.py 

to complete the installation of these software run: 

.. code:: sh

    cd ~
    source .profile
    source .bashrc

You can now use SCT. To use FSLeyes, run Xming from your computer before entering the fsleyes command.

Your local C drive is located under '/mnt/c'. You can access it by running 

.. code:: sh

    cd /mnt/c


 
