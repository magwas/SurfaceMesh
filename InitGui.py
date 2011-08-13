# coding=UTF-8

#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2011 Árpád Magosányi <mag@magwas.rulez.org>             * 
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU General Public License (GPL)            *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Library General Public License for more details.                  *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with this program; if not, write to the Free Software   *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************

__title__="FreeCAD Surface Editing Workbench - Init file"
__author__ = "Árpád Magosányi <mag@magwas.rulez.org>"
__url__ = ["http://free-cad.sourceforge.net"]

class SurfaceEditingWorkbench (Workbench): 
    MenuText = "Surface Mesh Editing"
    def Initialize(self):
        import SurfaceEditing 
        list = ["Add Mesh", "Insert Points", "Move Points", "Toggle Crease", "Add Property", "Add Edge", "Add Face", 'Clear Selection'] 
        self.appendToolbar("Surface Editing",list) 
        
Gui.addWorkbench(SurfaceEditingWorkbench())
