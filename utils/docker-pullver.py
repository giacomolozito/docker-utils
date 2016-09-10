#!/usr/bin/env python
#
# Docker-pullver is a script that allows user to specify a docker repository and a tag,
# then it contacts docker hub and identifies all images which have the same layer/ID as the one specified.
#
# This is useful when working with images which have been pushed to docker hub with multiple tags 
# and to be able to pick the most meaningful tags for deployments (i.e. the tag displaying a version or git commit).
#
# Uses Docker HUB API v1 (https://docs.docker.com/v1.7/docker/reference/api/docker-io_api/)
#
# Giacomo.Lozito@gmail.com 2016/03 - released under GPLv3

import sys
import os
import httplib
import getopt
import getpass, base64
import json
import subprocess


def _print_usage():
	print "TODO"


if __name__ == "__main__":

	try:
		opts, args = getopt.getopt(sys.argv[1:], "cpu:", ["use-config", "pull", "username="])
		if len(args) < 1: raise Exception('Insufficient number of arguments')
	except Exception as e:
		print str(e)
		_print_usage()
		sys.exit(1)

	docker_repo, docker_tag = args[0].split(':', 1) if ':' in args[0] else (args[0], "latest")
	docker_use_config, docker_build_login, docker_do_pull = False, False, False
	docker_username = None
	docker_auth = None

	for opt,arg in opts:
		if opt in ('-c','--use-config'):
			docker_use_config = True
		elif opt in ('-p','--pull'):
			docker_do_pull = True
		elif opt in ('-u','--username'):
			docker_build_login = True
			docker_username = arg
	
	if docker_use_config:
		docker_user_cfg = os.path.expanduser('~')+'/.docker/config.json'
		if os.path.exists(docker_user_cfg):
			with open(docker_user_cfg) as duc:
				docker_auth = json.load(duc)["auths"]["https://index.docker.io/v1/"]["auth"]
		else:
			print 'Use-config specified, but file %s was not found' % (docker_user_cfg)
			sys.exit(2)

	if docker_build_login:
		docker_passwd = getpass.getpass('Please input password for user %s : ' % (docker_username))
		docker_auth = base64.b64encode('%s:%s' % (docker_username, docker_passwd))

	# request the tags list from docker.io
	conn = httplib.HTTPSConnection('registry.hub.docker.com', 443)
	headers = { 'Authorization': 'Basic %s' % (docker_auth) }
	conn.request("GET", "/v1/repositories/%s/tags" % (docker_repo), "", headers)
	response = conn.getresponse()

	if str(response.status)[:2] != "20":
		print "Request failed, return code %s with reason %s" % (response.status, response.reason)
		sys.exit(3)

	repo_tags = json.loads(response.read())

	# find the requested tag among the available ones (note: returns a list but only one should be found)
	found_tag_list = filter(lambda x: x["name"] == docker_tag, repo_tags)
	if not found_tag_list:
		print "Tag %s was not found in repo %s" % (docker_tag, docker_repo)
		sys.exit(4)
	# find the same layer given by a different tag
	found_tag_same_list = filter(lambda x: x["layer"] == found_tag_list[0]["layer"] and x["name"] != docker_tag, repo_tags)
	if not found_tag_same_list:
		print "Tag %s was found in repo %s , but no images with same layer have been found" % (docker_tag, docker_repo)
		sys.exit(5)

	# if pull has not been requested, just print images list
	#print "Versioned Images with same layer as tag %s" % (docker_tag)
	#print "----------------------------------------%s" % ('-' * len(docker_tag))
	for found_tag_same in found_tag_same_list:
		print docker_repo + ':' + found_tag_same["name"]

	# if pull has been requested, pick the first one of the images with same layer
	if docker_do_pull:
		try:
			docker_cmd = ['docker','pull','%s:%s' % (docker_repo, found_tag_same_list[0]["name"])]
			docker_p = subprocess.Popen(docker_cmd, stdout=subprocess.PIPE)
			while docker_p.poll() is None:
				print docker_p.stdout.readline().strip()
			print docker_p.stdout.read().strip()
		except Exception as e:
			print "An error occurred: %s" % (str(e))
			print "Please try to run docker-pullver without -p/--pull and pull the reported image using docker command"
			sys.exit(6)

	sys.exit(0)
