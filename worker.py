#!/usr/bin/python -tt

import sys
import yum
import createrepo
import os
import rpmUtils
from optparse import OptionParser


# pass in dir to make tempdirs in
# make tempdir for this worker
# create 3 files in that tempdir
# return how many pkgs
# return on stderr where things went to hell

#TODO - take most of read_in_package from createrepo and duplicate it here
# so we can do downloads, etc.
# then replace callers of read_in_package with forked callers of this
# and reassemble at the end

def main(args):
    parser = OptionParser()
    parser.add_option('--tmpmdpath', default=None, 
                help="path where the outputs should be dumped for this worker")
    parser.add_option("--pkgoptions", default=[], action='append',
                help="pkgoptions in the format of key=value")

    
    opts, pkgs = parser.parse_args(args)
    external_data = {'_packagenumber': 0}
    if not opts.tmpmdpath:
        print >> sys.stderr, "tmpmdpath required for destination files"
        sys.exit(1)
    
    for strs in opts.pkgoptions:
        k,v = strs.split('=')
        if v in ['True', 'true', 'yes', '1', 1]:
            v = True
        elif v in ['False', 'false', 'no', '0', 0]:
            v = False
        elif v in ['None', 'none', '']:
            v = None
        external_data[k] = v

    
    reldir = external_data['_reldir']
    ts = rpmUtils.transaction.initReadOnlyTransaction()
    pri = open(opts.tmpmdpath + '/primary.xml' , 'w')
    fl = open(opts.tmpmdpath  + '/filelists.xml' , 'w')
    other = open(opts.tmpmdpath  + '/other.xml' , 'w')
    
    for pkgfile in pkgs:
        pkgpath = reldir + '/' + pkgfile
        if not os.path.exists(pkgpath):
            continue

        try:
            pkg = createrepo.yumbased.CreateRepoPackage(ts, package=pkgpath, 
                                                        external_data=external_data)
            pri.write(pkg.xml_dump_primary_metadata())
            fl.write(pkg.xml_dump_filelists_metadata())
            other.write(pkg.xml_dump_other_metadata())
        except yum.Errors.YumBaseError, e:
            print >> sys.stderr, "Error: %s" % e
            continue
        else:
            external_data['_packagenumber']+=1
        
    pri.close()
    fl.close()
    other.close()
    print external_data['_packagenumber']
    
if __name__ == "__main__":
    main(sys.argv[1:])
