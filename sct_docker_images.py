#!/usr/bin/env python3
# -*- coding: utf-8 vi:noet
# Testing using Docker

import sys, io, os, logging, time, datetime, shutil, datetime, subprocess

import sct_docker


if sys.hexversion < 0x03030000:
    import pipes
    def list2cmdline(lst):
        return " ".join(pipes.quote(x) for x in lst)
else:
    import shlex
    def list2cmdline(lst):
        return " ".join(shlex.quote(x) for x in lst)


default_distros = (
 "ubuntu:14.04",
 "ubuntu:16.04",
 "ubuntu:18.04",
 #"debian:7" # has issues with fsleyes
 "debian:8",
 "debian:9",
 "fedora:25",
 "fedora:26",
 "fedora:27",
)

default_version = "master"

default_commands = (
)

def generate(distros=None, version=None, jobs=None, publish_under=None, generate_offline_sct_distro=False):
	"""
	"""

	if distros is None:
		distros = default_distros

	if version is None:
		version = default_version

	names = []
	for distro in distros:
		name = "sct-{}-{}".format(version, distro.replace(":", "-")).lower()

		name = sct_docker.generate(distro=distro, version=version,
		 name=name, commands=default_commands,
		 install_fsleyes=True,
		 #install_fsl=True,
		 configure_ssh=True,
		)

		names.append(name)


	from multiprocessing.pool import ThreadPool
	pool = ThreadPool(jobs)

	try:
		res = list()
		for name in names:

			cmd = [
			 "docker", "build", "-t", name, name,
			]

			promise = pool.apply_async(lambda x: subprocess.call(x), (cmd,))
			res.append(promise)

		errs = list()
		for name, promise in zip(names, res):
			err = promise.get()
			if err != 0:
				logging.error("{} failed with error code {}".format(name, err))
			errs.append(err)

		pool.close()
	except BaseException as e:
		print("Keyboard interrupt")
		pool.terminate()
		raise SystemExit(1)
	pool.join()

	failed = False
	for name, err in zip(names, errs):
		if err == 0:
			logging.info("{} finished successfully".format(name))
		else:
			logging.error("{} failed with error code {}".format(name, err))
			failed = True

	if failed:
		print(errs)
		logging.error("Not proceeding further as one distro failed")
		return 1

	if publish_under:
		for name in names:
			cmd = ["docker", "tag", name, "{}:{}".format(publish_under, name)]
			subprocess.call(cmd)
			cmd = ["docker", "push", "{}:{}".format(publish_under, name)]
			subprocess.call(cmd)

	if generate_offline_sct_distro:
		for name in names:
			cmd = ["bash", "-c", "docker run {} tar --directory=/home/sct --create ." \
			 " | gzip > offline-archive-{}.tar.gz".format(name, name)]
			subprocess.call(cmd)


if __name__ == "__main__":

	import argparse


	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)


	parser = argparse.ArgumentParser(
	 description="SCT + Docker Official Image Generation",
	)

	subparsers = parser.add_subparsers(
	 help='the command; type "%s COMMAND -h" for command-specific help' % sys.argv[0],
	 dest='command',
	)

	subp = subparsers.add_parser(
	 "generate",
	 help="Build a distro/version",
	)

	subp.add_argument("--distros",
	 nargs="+",
	 help="Distributions to test (docker image names)",
	 default=default_distros,
	)

	subp.add_argument("--version",
	 default=default_version,
	)

	subp.add_argument("--jobs",
	 type=int,
	 default=None,
	)

	subp.add_argument("--generate-offline-sct-distro",
	 action="store_true",
	 default=False,
	)

	subp.add_argument("--publish-under",
	 help="Where to publish on docker hub (x/y)",
	)

	try:
		import argcomplete
		argcomplete.autocomplete(parser)
	except:
		pass

	args = parser.parse_args()

	if args.command == "generate":
		res = generate(distros=args.distros, version=args.version,
		 generate_offline_sct_distro=args.generate_offline_sct_distro,
		 publish_under=args.publish_under,
		 jobs=args.jobs)
		raise SystemExit(res)

