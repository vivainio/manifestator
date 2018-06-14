import sys
from manifestator import Manifestator

m = Manifestator(__file__)

m.root(r"test")
m.add_dirs(["d1", "d2"])
m.prune(".*ignored.*")
m.main("manifest.txt", sys.argv)


#m.write_manifest("manifest.txt")
#m.compare_with_manifest("manifest.txt")