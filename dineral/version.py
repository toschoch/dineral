import pkg_resources

__version__ = str(pkg_resources.get_distribution("dineral")).split(' ')[-1]