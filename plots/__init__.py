import matplotlib as mpl

mpl.style.use(['seaborn-muted','seaborn-whitegrid'])
mpl.rcParams['grid.linestyle']=':'
mpl.rcParams['grid.color']='.8'
mpl.rcParams['legend.fancybox']=True
mpl.rcParams['legend.frameon']=True   # whether or not to draw a frame around legend
mpl.rcParams['legend.numpoints']=2   # whether or not to draw a frame around legend
mpl.rcParams['axes.grid']=True
mpl.rcParams['axes.edgecolor']='0.5'
mpl.rcParams['image.cmap']='viridis'
mpl.rcParams['legend.edgecolor']='0.5'

from api import Report
reporter = Report()