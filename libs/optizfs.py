import zfslib as zfs

class OptiZFS(object):
    def __init__(self, host="localhost"):
        self.host = host
        self.pools = {}

        conn = zfs.Connection(host)
        self.poolset = conn.load_poolset()

    def __list_pools(self):
        for k, v in self.poolset._pools.items():
            self.pools[v.name] = v

    def get_pools(self):
        self.__list_pools()
        return self.pools

    def __get_property(self, pool, property):
        return pool.get_property(property)

    def get_storage(self, pool):
        return self.__get_property(pool, "capacity")

    def get_mounted(self, pool):
        return self.__get_property(pool, "mounted")

    def get_mountpoint(self, pool):
        return self.__get_property(pool, "mountpoint")


# ##################### TESTING
# z = OptiZFS()
# pools = z.get_pools()
# for k,v in pools.items():
#     print("Name: ", k)
#     print("Mountpoint: ", z.get_mountpoint(v))
#     print("Mounted: ", z.get_mounted(v))
#     print("Storage: ", z.get_storage(v))
#     print("\n")