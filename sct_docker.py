#!/usr/bin/env python3
# -*- coding: utf-8 vi:noet

import sys, io, os, logging, time, datetime, shutil


def generate(distro="debian:7", version="3.1.1", commands=None, name=None,
 install_compilers=False,
 install_fsleyes=False, install_fsl=False, configure_ssh=True):
	"""
	:param distro: Distribution (Docker specification)
	:param version: SCT version
	:param commands: Commands to run as part of build
	:returns: name
	"""

	frag = """
FROM {distro}
	""".strip().format(**locals())

	if distro.startswith(("debian", "ubuntu")):
		frag += "\n" + """
RUN apt-get update
RUN apt-get install -y curl sudo

# For conda
RUN apt-get install -y bzip2

# For remote GUI access
RUN apt-get install -y xorg
RUN apt-get install -y openssh-server
	""".strip()

	elif distro in ("centos:6", "centos:7",):
		frag += "\n" + """
RUN yum update -y

RUN yum install -y curl sudo

# For conda
RUN yum install -y bzip2

# For remote GUI access
RUN yum install -y xorg-x11-twm xorg-x11-xauth
RUN yum install -y openssh-server

# For SCT
RUN yum install -y procps findutils which
RUN yum search libstdc
RUN yum install -y compat-libstdc++-33 libstdc++
	""".strip()

	elif distro.startswith(("fedora", "centos")):
		frag += "\n" + """
RUN dnf update -y

RUN dnf install -y curl sudo

# For conda
RUN dnf install -y bzip2

# For remote GUI access
RUN dnf install -y xorg-x11-twm xorg-x11-xauth
RUN dnf install -y openssh-server

# For SCT
RUN dnf install -y procps findutils which
RUN dnf search libstdc
RUN dnf install -y compat-libstdc++-33 libstdc++
	""".strip()



	frag += "\n" + """
RUN useradd -ms /bin/bash sct
RUN echo "sct ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
RUN echo "sct:sct" | chpasswd
USER sct
ENV HOME /home/sct
WORKDIR /home/sct
EXPOSE 22
	""".strip()


	if version in ("3.1.1", "3.1.0"):
		sct_dir = "/home/sct/sct_{}".format(version)
		frag += "\n" + """
RUN curl --location https://github.com/neuropoly/spinalcordtoolbox/archive/v{version}.tar.gz | gunzip | tar x && cd spinalcordtoolbox-{version} && yes | ./install_sct && cd - && rm -rf spinalcordtoolbox-{version}
		""".strip().format(**locals())
	else:
		sct_dir = "/home/sct/sct_dev"
		frag += "\n" + """
RUN curl --location https://github.com/neuropoly/spinalcordtoolbox/archive/{version}.tar.gz | gunzip | tar x && cd spinalcordtoolbox-{version}* && yes | ./install_sct && cd - && rm -rf spinalcordtoolbox-{version}*
		""".strip().format(**locals())

	frag += "\n" + """
ENV SCT_DIR {sct_dir}
	""".strip().format(**locals())

	frag += "\n" + """
# Get data for offline use
RUN bash -i -c "sct_download_data -d sct_example_data"
RUN bash -i -c "sct_download_data -d sct_testing_data"
	""".strip()


	if install_fsleyes or install_fsl or install_compilers:
		if distro.startswith(("debian", "ubuntu")):
			frag += "\n" + """
RUN sudo apt-get update
RUN sudo apt-get install -y build-essential
			""".strip()

		elif distro.startswith("fedora"):
			frag += "\n" + """
# sudo dnf groupinstall -y "Development Tools"
RUN sudo dnf install -y redhat-rpm-config gcc "gcc-c++"
			""".strip()

		elif distro.startswith("centos"):
			frag += "\n" + """
RUN sudo yum install -y redhat-rpm-config gcc "gcc-c++" make
			""".strip()

	if install_fsleyes:
		if distro in ("debian:7",):
			frag += "\n" + """
RUN sudo apt-get install -y libgtkmm-3.0-dev libgtkglext1-dev libgtk-3-dev
RUN sudo apt-get install -y libgstreamer0.10-dev libgstreamer-plugins-base0.10-dev
RUN sudo apt-get install -y libwebkitgtk-3.0-dev libwebkitgtk-dev
			""".strip()

		elif distro.startswith(("debian", "ubuntu")):
			frag += "\n" + """
RUN sudo apt-get install -y libgtkmm-3.0-dev libgtkglext1-dev
RUN sudo apt-get install -y libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev
RUN sudo apt-get install -y libwebkitgtk-3.0-dev libwebkitgtk-dev
			""".strip()

		elif distro in ("fedora:27",):
			frag += "\n" + """
RUN sudo dnf install -y gtkmm30-devel gtkglext-devel
RUN sudo dnf install -y gstreamer1-devel gstreamer1-plugins-base-devel
RUN sudo dnf install -y webkitgtk4-devel
			""".strip()

		elif distro.startswith("fedora"):
			frag += "\n" + """
RUN sudo dnf install -y gtkmm30-devel gtkglext-devel
RUN sudo dnf install -y gstreamer1-devel gstreamer1-plugins-base-devel
RUN sudo dnf install -y webkitgtk3-devel webkitgtk-devel
			""".strip()

		elif distro.startswith("centos"):
			frag += "\n" + """
RUN sudo yum install -y gtkmm30-devel gtkglext-devel freeglut-devel
RUN sudo yum install -y gstreamer1-devel gstreamer1-plugins-base-devel
RUN sudo yum install -y webkitgtk3-devel webkitgtk-devel
			""".strip()

	if install_fsl:
		if distro.startswith("fedora"):
			frag += "\n" + """
RUN sudo dnf install -y expat-devel libX11-devel mesa-libGL-devel zlib-devel
			""".strip()
		elif distro.startswith("centos"):
			frag += "\n" + """
RUN sudo yum install -y expat-devel libX11-devel mesa-libGL-devel zlib-devel
			""".strip()
		elif distro.startswith(("ubuntu", "debian")):
			frag += "\n" + """
RUN sudo apt-get install -y libexpat1-dev libx11-dev zlib1g-dev libgl1-mesa-dev
			""".strip()

	if install_fsleyes:
		frag += "\n" + """
RUN bash -i -c "$SCT_DIR/python/bin/pip install fsleyes"
		""".strip()

	if install_fsl:
		# TODO WIP
		# https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation/SourceCode
		# https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation/ShellSetup
		if False: #os.path.exists("fsl-5.0.11-sources.tar.gz"):
			frag += "\n" + """
COPY fsl-5.0.11-sources.tar.gz /home/sct/fsl-5.0.11-sources.tar.gz
RUN bash -c "tar xzf fsl-5.0.11-sources.tar.gz && rm fsl-5.0.11-sources.tar.gz"
			""".strip()#.format(os.getcwd())
		else:
			frag += "\n" + """
RUN bash -c "curl https://fsl.fmrib.ox.ac.uk/fsldownloads/fsl-5.0.11-sources.tar.gz | gunzip | tar x"
			""".strip()

		frag += "\n" + """
ENV FSLDIR /home/sct/fsl
RUN bash -c ". ${FSLDIR}/etc/fslconf/fsl.sh; ls ${FSLDIR}/config/\${FSLMACHTYPE}"
RUN bash -c ". ${FSLDIR}/etc/fslconf/fsl.sh; cd ${FSLDIR}; ./build"
RUN bash -c ". ${FSLDIR}/etc/fslconf/fsl.sh; ${FSLDIR}/etc/fslconf/post_install.sh -f ${FSLDIR}"
RUN bash -c ". ${FSLDIR}/etc/fslconf/fsl.sh; ${FSLDIR}/etc/fslconf/fslpython_install.sh"
RUN bash -c "echo -ne '. ${FSLDIR}/etc/fslconf/fsl.sh; PATH+=:${FSLDIR}/bin\n\n' >> ~/.bashrc"
RUN bash -c "cat ~/.bashrc"
		""".strip()

	if commands is not None:
		frag += "\n" + "\n".join(["""RUN bash -i -c '{}'""".format(command) for command in commands])

	if configure_ssh:

		if not distro.startswith(("ubuntu", "debian")):
			frag += "\n" + """
RUN yes '' | sudo ssh-keygen -q -t ed25519 -f /etc/ssh/ssh_host_ed25519_key
			""".strip()

		frag += "\n" + """
# QC connection
EXPOSE 8888

RUN echo  X11UseLocalhost no | sudo tee --append /etc/ssh/sshd_config

ENTRYPOINT bash -c 'sudo /usr/sbin/sshd; /bin/bash'
		""".strip()

	frag += "\n" + """
RUN echo Finished
	""".strip()


	if name is None:
		name = "sct-%s-%s" % (distro.replace(":", "-"), version)

	if not os.path.exists(name):
		os.makedirs(name)
	with io.open(os.path.join(name, "Dockerfile"), "w") as f:
		f.write(frag)

	logging.info("You can now run: docker build -t %s %s", name, name)

	return name


if __name__ == "__main__":

	import argparse


	logger = logging.getLogger()
	#logger.addHandler(logging.StreamHandler(sys.stdout))
	logger.setLevel(logging.DEBUG)#INFO)


	parser = argparse.ArgumentParser(
	 description="SCT + Docker",
	)

	subparsers = parser.add_subparsers(
	 help='the command; type "%s COMMAND -h" for command-specific help' % sys.argv[0],
	 dest='command',
	)

	subp = subparsers.add_parser(
	 "generate",
	 help="Generate a Docker file",
	)

	subp.add_argument("--distro",
	 default="ubuntu:16.04",
	 help="Distribution to use (docker image)",
	)

	subp.add_argument("--version",
	 default="3.1.1",
	)

	try:
		import argcomplete
		argcomplete.autocomplete(parser)
	except:
		pass

	args = parser.parse_args()

	if args.command == "generate":
		name = generate(distro=args.distro, version=args.version)
		print(name)

