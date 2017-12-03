import pkg_resources

try:
    __version__ = str(pkg_resources.get_distribution("dineral")).split(' ')[-1]

except pkg_resources.DistributionNotFound:
    __version__ = 'dev'