# The Spatial Processes in HYdrology (SPHY) model:
# A spatially distributed hydrological model that calculates soil-water and
# cryosphere processes on a cell-by-cell basis.
#
# Copyright (C) 2013  FutureWater
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Email: info@futurewater.nl

#-Authorship information-###################################################################
__author__ = "W. Terink, A. Lutz, G. Simons, W. Immerzeel and P. Droogers"
__copyright__ = "FutureWater"
__license__ = "GPL"
__version__ = "erosion testing"
__email__ = "info@futurewater.nl"
__date__ ='1 January 2017'
############################################################################################

#-Function to calculate rootzone runoff
def RootRunoff(self, pcr, rainfrac, rain):
    #-At the moment, only apply reduced infiltration rate if sediment module is used.
    if self.SedFLAG == 1:
        #-infiltration capacity, scaled based on rootwater content and ksat
        Infil_cap = self.RootKsat * (pcr.max(pcr.min(1, 1 - (self.RootWater - \
            self.RootDry)/(self.RootSat - self.RootDry)), 0))**self.Infil_alpha
    else: #-assume infiltration capacity to be equal to saturated hydraulic conductivity
        Infil_cap = self.RootKsat
    self.report(Infil_cap, self.outpath + 'InfCap')
    #-infiltration
    Infil = pcr.max(0, pcr.min(rain, Infil_cap, self.RootSat - self.RootWater))
    self.report(Infil, self.outpath + 'Infil')
    #-Runoff
    rootrunoff = pcr.ifthenelse(rainfrac > 0, rain - Infil, 0)
    #-Updated rootwater content
    self.RootWater = pcr.ifthenelse(rainfrac > 0, self.RootWater + Infil, self.RootWater)
    return rootrunoff, self.RootWater

#-Function to calculate rootzone drainage
def RootDrainage(pcr, rootwater, rootdrain, rootfield, rootsat, drainvel, rootTT):
    rootexcess = pcr.max(rootwater - rootfield, 0)
    rootexcessfrac = rootexcess / (rootsat - rootfield)
    rootlat = rootexcessfrac * drainvel
    rootdrainage = pcr.max(pcr.min(rootwater, rootlat * (1-pcr.exp(-1/rootTT)) + rootdrain * pcr.exp(-1/rootTT)), 0)
    return rootdrainage

#-Function to calculate rootzone percolation
def RootPercolation(pcr, rootwater, subwater, rootfield, rootTT, subsat):
    rootexcess = pcr.max(rootwater - rootfield, 0)
    rootperc = rootexcess * (1 - pcr.exp(-1 / rootTT))
    rootperc = pcr.ifthenelse(subwater >= subsat, 0, pcr.min(subsat - subwater, rootperc))
    rootperc = pcr.max(pcr.min(rootperc, rootwater), 0)
    return rootperc
