#!/usr/bin/env python3
# Copyright (C) 2013-2014 Florian Festi
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from boxes import *
import math


class FlexBox3(Boxes):
    """Box with living hinge"""

    ui_group = "FlexBox"

    def __init__(self):
        Boxes.__init__(self)
        self.addSettingsArgs(edges.FingerJointSettings, surroundingspaces=1)
        self.addSettingsArgs(edges.FlexSettings)
        self.buildArgParser("x", "y", "outside")
        self.argparser.add_argument(
            "--z", action="store", type=float, default=100.0,
            help="height of the box")
        self.argparser.add_argument(
            "--h", action="store", type=float, default=10.0,
            help="height of the lid")
        self.argparser.add_argument(
            "--radius", action="store", type=float, default=10.0,
            help="radius of the lids living hinge")
        self.argparser.add_argument(
            "--c", action="store", type=float, default=1.0,
            dest="d", help="clearance of the lid")

    def rectangleCorner(self, edge1=None, edge2=None):
        edge1 = self.edges.get(edge1, edge1)
        edge2 = self.edges.get(edge2, edge2)
        if edge2:
            self.edge(edge2.startwidth())
        self.corner(90)
        if edge1:
            self.edge(edge1.endwidth())

    @restore
    def flexBoxSide(self, x, y, r, callback=None):
        self.cc(callback, 0)
        self.edges["f"](x)
        self.corner(90, 0)
        self.cc(callback, 1)
        self.edges["f"](y - r)
        self.corner(90, r)
        self.cc(callback, 2)
        self.edge(x - r)
        self.corner(90, 0)
        self.cc(callback, 3)
        self.edges["f"](y)
        self.corner(90)

    def surroundingWall(self):
        x, y, z, r, d = self.x, self.y, self.z, self.radius, self.d

        self.edges["F"](y - r, False)
        self.edges["X"](self.c4, z + 2 * self.thickness)
        self.corner(-90)
        self.edge(d)
        self.corner(90)
        self.edges["f"](x - r + d)
        self.corner(90)
        self.edges["f"](z + 2 * self.thickness + 2 * d)
        self.corner(90)
        self.edges["f"](x - r + d)
        self.corner(90)
        self.edge(d)
        self.corner(-90)
        self.edge(self.c4)
        self.edges["F"](y - r)
        self.corner(90)
        self.edge(self.thickness)
        self.edges["f"](z)
        self.edge(self.thickness)
        self.corner(90)

    @restore
    def lidSide(self):
        x, y, z, r, d, h = self.x, self.y, self.z, self.radius, self.d, self.h
        t = self.thickness
        r2 = r + t if r + t <= h + t else h + t
        self.moveTo(self.thickness, 0)
        if r < h:
            r2 = r + t
            self.edge(h + self.thickness - r2)
            self.corner(90, r2)
            self.edge(r - r2 + 2 * t)
            base_l = x + 2 * t
        else:
            a = math.acos((r-h)/(r+t))
            ang = math.degrees(a)
            base_l = x + (r+t) * math.sin(a) - r
            self.corner(90-ang)
            self.corner(ang, r+t)

        self.edges["F"](x - r)
        self.rectangleCorner("F", "f")
        self.edges["g"](h)
        self.rectangleCorner("f", "e")
        self.edge(base_l)
        self.corner(90)

    def render(self):
        if self.outside:
            self.x = self.adjustSize(self.x)
            self.y = self.adjustSize(self.y)
            self.z = self.adjustSize(self.z)

        x, y, z, d, h = self.x, self.y, self.z, self.d, self.h
        r = self.radius = self.radius or min(x, y) / 2.0
        thickness = self.thickness

        self.c4 = c4 = math.pi * r * 0.5 * 0.95
        self.latchsize = 8 * thickness

        width = 2 * x + y - 2 * r + c4 + 14 * thickness + 3 * h  # lock
        height = y + z + 8 * thickness

        self.open()

        s = edges.FingerJointSettings(self.thickness, finger=1.,
                                      space=1., surroundingspaces=1)
        s.edgeObjects(self, "gGH")

        self.moveTo(2 * self.thickness, self.thickness + 2 * d)
        self.ctx.save()
        self.surroundingWall()
        self.moveTo(x + y - 2 * r + self.c4 + 2 * self.thickness, -2 * d - self.thickness)
        self.rectangularWall(x, z, edges="FFFF", move="right")
        self.rectangularWall(h, z + 2 * (d + self.thickness), edges="GeGF", move="right")
        self.lidSide()
        self.moveTo(2 * h + 5 * self.thickness, 0)
        self.ctx.scale(-1, 1)
        self.lidSide()

        self.ctx.restore()
        self.moveTo(0, z + 4 * self.thickness + 2 * d)
        self.flexBoxSide(x, y, r)
        self.moveTo(2 * x + 3 * self.thickness, 2 * d)
        self.ctx.scale(-1, 1)
        self.flexBoxSide(x, y, r)
        self.ctx.scale(-1, 1)
        self.moveTo(2 * self.thickness, -self.thickness)
        self.rectangularWall(z, y, edges="fFeF")

        self.close()


