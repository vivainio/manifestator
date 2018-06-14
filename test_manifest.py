import sys
from manifestator import Manifestator

m = Manifestator(__file__)

m.root(r".")
m.add_dirs(["."])
m.prune(".*ignored.*")
m.prune("^./.git.*")
m.prune(".*pyc")

m.main("manifest.txt", sys.argv)


#m.write_manifest("manifest.txt")
#m.compare_with_manifest("manifest.txt")