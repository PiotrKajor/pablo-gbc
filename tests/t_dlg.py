import sys; sys.path.insert(0,'tests')
from lib import *
g = Game(save=(1, 4, 12, 1, 5))
g.tick(150); g.tap('start', 4); g.tick(150)
g.tap('up', 3); g.tick(20)
g.shot('dlg_tab1'); g.tick(90); g.shot('dlg_tab2')
g.tap('a',3); g.tick(120); g.shot('dlg_tab3')
