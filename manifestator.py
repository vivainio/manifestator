from __future__ import print_function

import os,sys,glob,re,time
from argparse import ArgumentParser
from os.path import join,abspath

def parse_head(line):
    parts_raw = (l.strip().split("=",1) for l in line.split(';'))
    parts = { key: value.split(",") for (key, value) in parts_raw}
    return parts

def expand_dirs(root, dirs):
    expanded = set()
    os.chdir(root)
    for d in dirs:
        for fpath, _, files in os.walk(d):
            fpath = fpath.replace("\\", "/")
            expanded.update(set(fpath+"/" + fname for fname in files))

    return expanded

def manifested_files(f):
    return set(l.strip() for l in f)

def report_files(files):
    print("\n".join("- " + l for l in sorted(files)))

def report_diffs(manifested_set, found_set):
    missing = manifested_set.difference(found_set)
    new = found_set.difference(manifested_set)

    if new:
        print("WARNING(MW1): Files new in build, but not (yet?) in manifest (did you forget to prune?):")
        report_files(new)
    if missing:
        print("WARNING(MW2): Files listed in manifest but MISSING from build:")
        report_files(missing)

    if missing or new:
        return (missing,new)
    return None

class Manifestator:
    def __init__(self, file):
        self._startRoot = os.path.dirname(abspath(file))
        self._script = abspath(file)
        self._coll = set()
        self._start = time.time()
    def root(self, reldir):
        self._root = abspath(join(self._startRoot, reldir))

    def add_dirs(self, dirs):
        self._coll.update(expand_dirs(self._root, dirs))

    def manifest_filename(self, fname):
        return abspath(join(self._startRoot, fname))

    def write_manifest(self, fname):
        print("Writing manifest %s (%d lines)" % (abspath(fname), len(self._coll)))
        open(fname, "w").write("\n".join(sorted(self._coll)))

    def compare_with_manifest(self, fname):
        manifested = manifested_files(open(fname))
        return report_diffs(manifested, self._coll)
    def prune(self, regex):
        pat = re.compile(regex)
        self._coll = set(f for f in self._coll if not pat.match(f))


    def main(self, manifest, argv):
        s = self._main(manifest, argv)
        print("Manifestator took %.0fms" % ((time.time() - self._start) * 1000))
        sys.exit(s)

    def _main(self, manifest, argv):

        a = ArgumentParser()
        a.add_argument("--rewrite", action="store_true", help="Rewrite the manifest")
        parsed = a.parse_args()
        os.chdir(self._startRoot)
        if parsed.rewrite:
            self.write_manifest(manifest)
            return 0

        if not os.path.isfile(manifest):
            print("ERROR(ME1): Manifest not found in '%s', bailing out. Create one with --rewrite" % abspath(manifest))
            return 1

        reports = self.compare_with_manifest(manifest)

        if reports:
            print("If you think manifest is obsolete, you can recreate it with 'python %s --rewrite'" % self._script)
        else:
            print("Manifest OK:",abspath(manifest))
