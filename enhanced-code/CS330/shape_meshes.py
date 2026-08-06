# *****CODE INFORMATION*****
# Name: Michael King
# Date: 7/17/2026
# File: shape_meshes.py
# Assignment: CS-499 Enhancement 1
# CS-330 3D Scene Python Port
# University: SNHU

# Python Port of ShapeMeshes.h/ShapeMeshes.cpp from CS-330 (C++/OpenGL).
# ORIGINALLY MADE BY: Brian Battersby (SNHU Instructor).
# MODIFIED BY: Michael King
# Adapted for CS-499 Software Engineering Enhancement by Michael King
# PORTED TO PYTHON/PyOpenGL BY: Michael King

# Each mesh follows the vertex layout established by SetShaderMemoryLayout():
#   Attribute 0: position (3 floats, stride byte-offset 0)
#   Attribute 1: normal   (3 floats, stride byte-offset 12)
#   Attribute 2: texCoord (2 floats, stride byte-offset 24)
#   Total stride: 8 floats x 4 bytes = 32 bytes per vertex
# 
# The C++ implementation stores raw vertex arrays in source code.
# This Python port uses the same literal data for indexed meshes (box, plane)
# and generates curved shapes (cylinder, torus, tapered cylinder) procedurally,
# which is cleaner, more readable, and easier to tune.
# 
# DESIGN DIFFERENCE FROM C++:
# The C++ class stored GLMesh structs with vao, vbos[], nVertices, nIndices.
# Python uses a simple dataclass-style dict per mesh, and the VAO/VBO setup is
# handled inside each load method rather than in a shared template function.
# The memory layout (glVertexAttribPointer calls) is applied once per VAO,
# matching the m_bMemoryLayoutDone guard in the original SetShaderMemoryLayout().

# *** Python Imports ***
import math
import ctypes
import numpy as np

from OpenGL.GL import (
    glGenVertexArrays, glBindVertexArray,
    glGenBuffers, glBindBuffer, glBufferData,
    glVertexAttribPointer, glEnableVertexAttribArray,
    glDrawArrays, glDrawElements,
    GL_ARRAY_BUFFER, GL_ELEMENT_ARRAY_BUFFER,
    GL_STATIC_DRAW, GL_FLOAT, GL_FALSE,
    GL_TRIANGLES, GL_UNSIGNED_INT,
)

# *********************************************************
# VERTEX LAYOUT CONSTANTS; 
# must match the GLSL attribute locations
# *********************************************************

FLOATS_PER_VERTEX = 3 #x, y, z
FLOATS_PER_NORMAL = 3 #nx, ny, nz
FLOATS_PER_UV     = 2 #u, v
FLOATS_PER_VERT   = FLOATS_PER_VERTEX + FLOATS_PER_NORMAL + FLOATS_PER_UV # 8
STRIDE            = FLOATS_PER_VERT * 4 # 32 bytes

def _setup_vao(verts: np.ndarray, indices: np.ndarray = None) -> dict:
    '''
    Upload vertex (and optional index) data to the GPU and configure the
    attribute pointers for the shared layout (position, normal, UV).

    Mirrors the inline VAO/VBO setup found at the bottom of each LoadXxxMesh()
    in shapeMeshes.cpp, plus the SetShaderMemoryLayout() call.

    Args:
    verts........Float32 array of interleaved vertex data (pos/normal/uv).
    indices......Optional uint32 index array for indexed drawing.

    Returns:
    A dict with 'vao', optional 'ebo', 'n_verts', and 'n_indices'.
    '''
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, GL_STATIC_DRAW)

    ebo = None
    if indices is not None:
        ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    # Attribute 0: position (3 floats at offset 0)
    glVertexAttribPointer(0, FLOATS_PER_VERTEX, GL_FLOAT, GL_FALSE, STRIDE, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

     # Attribute 1: normal (3 floats at offset 12)
    glVertexAttribPointer(1, FLOATS_PER_UV, GL_FLOAT, GL_FALSE, STRIDE, 
                          ctypes.c_void_p(FLOATS_PER_VERTEX * 4))
    glEnableVertexAttribArray(1)

     # Attribute 2: UV coords (2 floats at offset 24)
    glVertexAttribPointer(2, FLOATS_PER_UV, GL_FLOAT, GL_FALSE, STRIDE, 
                          ctypes.c_void_p((FLOATS_PER_VERTEX + FLOATS_PER_NORMAL) * 4))
    glEnableVertexAttribArray(2)

    glBindVertexArray(0)

    return {
        "vao": vao,
        "vbo": vbo,
        "ebo": ebo,
        "n_verts": len(verts) //FLOATS_PER_VERT,
        "n_indices": len(indices) if indices is not None else 0,
    }

class ShapeMeshes:
    '''
    Loads primitive 3D mesh data into OpenGL VAOs and provides draw calls.

    Ported from ShapeMeshes.h/ShapeMeshes.cpp (C++).
    Each Load*() method must be called once during scene preparation;
    Draw*() method can then be called any number of times per frame.
    '''

    def __init__(self):
        '''Initialize all mesh handles to None.
        Meshes are loaded on demand.'''
        self._box         = None
        self._plane       = None
        self._cylinder    = None
        self._torus       = None
        self._tapered_cyl = None

    # *********************************************************
    # ----------------- PLANE MESH -----------------
    # A flat 2x2 quad in the XZ plane, normal pointing +Y.
    # Exact vertex data from
    # ShapeMeshes.cpp::LoadPlaneMesh().
    # Drawn with glDrawElements (indexed).
    # *********************************************************

    def load_plane_mesh(self):
        '''
        Load the plane mesh (table surface into GPU memory).

        Vertex data matches the C++ LoadPlaneMesh() exactly:
        A 2x2 quad centered at the origin, lying flat in XZ, normal = +Y.
        The model matrix in SceneManager scales it to the desired world size.
        '''
        verts = np.array([
        #     x    y     z     nx    ny    nz    u     v
            -1.0, 0.0,  1.0,  0.0,  1.0,  0.0,  0.0,  0.0,  #0
             1.0, 0.0,  1.0,  0.0,  1.0,  0.0,  1.0,  0.0,  #1
             1.0, 0.0, -1.0,  0.0,  1.0,  0.0,  1.0,  1.0,  #2
            -1.0, 0.0, -1.0,  0.0,  1.0,  0.0,  0.0,  1.0,  #3
        ], dtype=np.float32)

        indices = np.array([0, 1, 2, 0, 3, 2], dtype=np.uint32)

        self._plane = _setup_vao(verts, indices)

    def draw_plane_mesh(self):
        '''draw the plane mesh using the indexed triangles'''
        if self._plane is None:
            return
        glBindVertexArray(self._plane["vao"])
        glDrawElements(GL_TRIANGLES, self._plane["n_indices"], GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

    # *********************************************************
    # ----------------- BOX MESH -----------------
    # A unit cube centered at the origin.
    # Exact vertex/index data from
    # ShapeMeshes.cpp::LoadBoxMesh().
    # *********************************************************

    def load_box_mesh(self):
        '''
        Load the box mesh(cutting board, fork, knife) into GPU memory.

        24 unique vertices (4 per face x 6 faces) with per-face normals.
        Drawn with glDrawElements (indexed), 12 triangles = 36 indices.
        '''

        verts = np.array([
        #   Back face (normal: 0, 0, -1)
            0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  0.0,  1.0,
            0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  0.0,  0.0,
           -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  1.0,  0.0,
           -0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  1.0,  1.0,
        #   Bottom face (normal 0, -1, 0)
           -0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  0.0,  1.0,
           -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  0.0,  0.0,
            0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  1.0,  0.0,
            0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  1.0,  1.0,
        #   Left face (normal: -1, 0, 0)
           -0.5,  0.5, -0.5, -1.0,  0.0,  0.0,  0.0,  1.0,
           -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,  0.0,  0.0,
           -0.5, -0.5,  0.5, -1.0,  0.0,  0.0,  1.0,  0.0,
           -0.5,  0.5, -0.5, -1.0,  0.0,  0.0,  1.0,  1.0,
        #   Right face (normal: +1, 0, 0)
            0.5,  0.5,  0.5,  1.0,  0.0,  0.0,  0.0,  1.0,
            0.5, -0.5,  0.5,  1.0,  0.0,  0.0,  0.0,  0.0,
            0.5, -0.5, -0.5,  1.0,  0.0,  0.0,  1.0,  0.0,
            0.5,  0.5, -0.5,  1.0,  0.0,  0.0,  1.0,  1.0,
        #   Top face (normal: 0, +1, 0)
           -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  0.0,  1.0,
           -0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  0.0,  0.0,
            0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  1.0,  0.0,
            0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  1.0,  1.0,
        #   Front face (normal: 0, 0, +1)
           -0.5,  0.5,  0.5,  0.0,  0.0,  1.0,  0.0,  1.0,
           -0.5, -0.5,  0.5,  0.0,  0.0,  1.0,  0.0,  0.0,
            0.5, -0.5,  0.5,  0.0,  0.0,  1.0,  1.0,  0.0,
            0.5,  0.5,  0.5,  0.0,  0.0,  1.0,  1.0,  1.0,
        ], dtype=np.float32)

        indices = np.array([
            0,  1,  2,  0,  3,  2,
            4,  5,  6,  4,  7,  6,
            8,  9,  10, 8,  11, 10,
            12, 13, 14, 12, 15, 14,
            16, 17, 18, 16, 19, 18,
            20, 21, 22, 20, 23, 22,
        ], dtype=np.uint32)

        self._box = _setup_vao(verts, indices)

    def draw_box_mesh(self):
        '''draw the box mesh using indexed triangles.'''
        if self._box is None:
            return
        glBindVertexArray(self._box["vao"])
        glDrawElements(GL_TRIANGLES, self._box["n_indices"], GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

    # *********************************************************
    # ----------------- CYLINDER MESH -----------------
    # Procedurally generated open-ended cylinder
    # (unit radius, unit height).
    # Equivalent to the large literal array in
    # LoadCylinderMesh().
    # *********************************************************

    def load_cylinder_mesh(self, sectors: int=36):
        '''
        Procedurally generate and upload a cylinder mesh.

        The C++ version uses a hand-authored triangle-strip array.
        This Python port generates the same geometry procedurally, which is
        equivalent in output but more readable and parameterizable.

        The cylinder has unit radius and height, centered vertically at y=0.5
        (base at y=0, cap at y=1), matching the C++ convention.

        ARGS:
        sectors: number of angular subdivisions around the cylinder.
        36 matches the C++ version's level of detail.
        '''
        verts=[]

        # ---Bottom cap (Center at y=0, normal = -Y) ---
        center_b = [0.0, 0.0, 0.0,   0.0, -1.0, 0.0,  0.5, 0.5]
        for i in range(sectors):
            a0 = 2.0 * math.pi * i / sectors
            a1 = 2.0 * math.pi * (i + 1) / sectors
            x0, z0 = math.cos(a0), math.sin(a0)
            x1, z1 = math.cos(a1), math.sin(a1)
            #Triangle: center, current rim, next rim
            verts += center_b
            verts += [x0, 0.0, z0,  0.0, -1.0, 0.0,  0.5 + 0.5*x0, 0.5 + 0.5*z0]
            verts += [x1, 0.0, z1,  0.0, -1.0, 0.0,  0.5 + 0.5*x1, 0.5 + 0.5*z1]

        # ---Top cap (Center at y=1, normal = +Y) ---
        center_t = [0.0, 1.0, 0.0,   0.0, 1.0, 0.0,  0.5, 0.5]
        for i in range(sectors):
            a0 = 2.0 * math.pi * i / sectors
            a1 = 2.0 * math.pi * (i + 1) / sectors
            x0, z0 = math.cos(a0), math.sin(a0)
            x1, z1 = math.cos(a1), math.sin(a1)
            #Triangle: center, current rim, next rim
            verts += center_t
            verts += [x1, 1.0, z1,  0.0, 1.0, 0.0,  0.5 + 0.5*x1, 0.5 + 0.5*z1]
            verts += [x0, 1.0, z0,  0.0, 1.0, 0.0,  0.5 + 0.5*x0, 0.5 + 0.5*z0]

        # ---Side wall (normals point radially outward)
        for i in range(sectors):
            a0 = 2.0 * math.pi * i / sectors
            a1 = 2.0 * math.pi * (i + 1) / sectors
            x0, z0 = math.cos(a0), math.sin(a0)
            x1, z1 = math.cos(a1), math.sin(a1)
            u0 = i / sectors
            u1 = (i + 1) / sectors
            # Two triangles per quad strip sections
            verts += [x0, 0.0, z0,  x0, 0.0, z0,  u0, 0.0]
            verts += [x1, 0.0, z1,  x1, 0.0, z1,  u1, 0.0]
            verts += [x1, 1.0, z1,  x1, 0.0, z1,  u1, 1.0]
            verts += [x0, 0.0, z0,  x0, 0.0, z0,  u0, 0.0]
            verts += [x1, 1.0, z1,  x1, 0.0, z1,  u1, 1.0]
            verts += [x0, 1.0, z0,  x0, 0.0, z0,  u0, 1.0]

        arr = np.array(verts, dtype=np.float32)
        self._cylinder = _setup_vao(arr)
        self._cylinder_sectors = sectors
    
    def draw_cylinder_mesh(self, draw_top=True, draw_bottom=True, draw_sides=True):
        '''
        Draw the cylinder mesh.

        SECTIONS:
        [bottom caps] + [top caps] + [side quads]
        draw_top/bottom/sides flags match the C++ DrawCylinderMesh() signature.

        ARGS:
        draw_top............Render the top cap
        draw_bottom.........Render the bottom cap
        draw_sides..........Render the sides
        '''
        if self._cylinder is None:
            return
        
        #Sector count stored at load time (default 36)
        sectors = getattr(self, '_cylinder_sectors', 36)
        glBindVertexArray(self._cylinder["vao"])

        #Bottom cap occupies first sectors*3 vertices
        if draw_bottom:
            glDrawArrays(GL_TRIANGLES, 0, sectors * 3)
        #Top cap follows the bottom cap
        if draw_top:
            glDrawArrays(GL_TRIANGLES, sectors * 3, sectors * 3)
        #Side wall: 6 vertices per sector quad
        if draw_sides:
            glDrawArrays(GL_TRIANGLES, sectors * 6, sectors * 6)

        glBindVertexArray(0)

    # *********************************************************
    # ----------------- TORUS MESH -----------------
    # Procedurally generated torus
    # (donut shape for the mug handle).
    # Equivalent to the triangle array in
    # LoadTorusMesh().
    # *********************************************************

    def load_torus_mesh(self, thickness: float = 0.1, main_r: float = 0.5,
                        main_segs: int = 36, tube_segs: int = 18):
        '''
        Procedurally generate and upload a torus mesh.

        The C++ version uses a hand-authored large vertex array.
        This Python port generates the same shape procedurally.

        ARGS:
        thickness......Radius of the tube cross-section.
                       Matches C++ default 0.2.
        main_r.........Radius from torus center to tube center.
        main_segs......number of segments around the main ring.
        tube_segs......number of segments around the tube cross-section.
        '''
        verts = []

        for i in range(main_segs):
            for j in range(tube_segs):
                #Angle increments for main ring and tube cross-section
                u0 = 2.0 * math.pi * i / main_segs
                u1 = 2.0 * math.pi * (i + 1) / main_segs
                v0 = 2.0 * math.pi * j / tube_segs
                v1 = 2.0 * math.pi * (j + 1) / tube_segs

                def vertex(u, v):
                    '''compute a single torus vertex position and outward normal.'''
                    cos_u, sin_u = math.cos(u), math.sin(u)
                    cos_v, sin_v = math.cos(v), math.sin(v)
                    x = (main_r + thickness * cos_v) * cos_u
                    y = thickness * sin_v
                    z = (main_r + thickness * cos_v) * sin_u
                    # normal points from the tube center outward through the surface

                    nx = cos_v * cos_u
                    ny = sin_v
                    nz = cos_v * sin_u
                    # UV: u wraps around the ring, v wraps around the tube
                    tu = i / main_segs
                    tv = j / tube_segs
                    return [ x, y, z, nx, ny, nz, tu, tv ]
                
                # Two triangles per quad
                p00 = vertex(u0, v0)
                p10 = vertex(u1, v0)
                p01 = vertex(u0, v1)
                p11 = vertex(u1, v1)
                verts += p00 + p10 + p11
                verts += p00 + p11 + p01
            
        arr = np.array(verts, dtype=np.float32)
        self._torus = _setup_vao(arr)
    
    def draw_torus_mesh(self):
        '''draw the full torus mesh.'''
        if self._torus is None:
            return
        glBindVertexArray(self._torus["vao"])
        glDrawArrays(GL_TRIANGLES, 0, self._torus["n_verts"])
        glBindVertexArray(0)
    

    # *********************************************************
    # ----------------- TAPERED CYLINDER MESH -----------------
    # Like a cylinder but with a smaller top radius
    # (for the ramekin bowl).
    # Equivalent to LoadTaperedCylinderMesh() in C++
    # *********************************************************

    def load_tapered_cylinder_mesh(self, top_r: float = 0.5, bot_r: float = 1.0,
                                   sectors: int = 36):
        '''
        Procedurally generate and upload a tapered cylinder mesh.

        A tapered cylinder is wider at the bottom than the top (or vice versa),
        making it ideal for approximating bowl or cup shapes.
        The C++ version uses top_radius=0.5 and bot_radius=1.0
        (wider at bottom).

        The ramekin in the scene is drawn with a 180-degree X-rotation,
        so the wide end faces upward, giving it the natural bowl silhouette.

        ARGS:
        top_r..........Radius of the top circle
        bot_r..........Radius of the bottom circle.
        sectors........Angular subdivisions.
        '''
        verts = []

        # --- Bottom cap (normal = -Y) ---
        for i in range(sectors):
            a0 = 2.0 * math.pi * i / sectors
            a1 = 2.0 * math.pi * (i + 1) / sectors
            x0, z0 = bot_r * math.cos(a0), bot_r * math.sin(a0)
            x1, z1 = bot_r * math.cos(a1), bot_r * math.sin(a1)
            verts += [0.0, 0.0, 0.0,  0.0, -1.0, 0.0,   0.5, 0.5]
            verts += [x0, 0.0, z0,  0.0, -1.0, 0.0,  0.5 + 0.5*(x0/bot_r), 0.5 + 0.5*(z0/bot_r)]
            verts += [x1, 0.0, z1,  0.0, -1.0, 0.0,  0.5 + 0.5*(x1/bot_r), 0.5 + 0.5*(z1/bot_r)]

        # --- Top cap (normal = +Y) ---
        for i in range(sectors):
            a0 = 2.0 * math.pi * i / sectors
            a1 = 2.0 * math.pi * (i + 1) / sectors
            x0, z0 = bot_r * math.cos(a0), bot_r * math.sin(a0)
            x1, z1 = bot_r * math.cos(a1), bot_r * math.sin(a1)
            verts += [0.0, 1.0, 0.0,  0.0, 1.0, 0.0,   0.5, 0.5]
            verts += [x1, 0.0, z1,  0.0, 1.0, 0.0,  0.5 + 0.5*(x1/bot_r), 0.5 + 0.5*(z1/bot_r)]
            verts += [x0, 0.0, z0,  0.0, 1.0, 0.0,  0.5 + 0.5*(x0/bot_r), 0.5 + 0.5*(z0/bot_r)]

        # --- Side wall (normal computed per vertex, angled for taper) ---
        # the slant normal is the average of the inward taper direction and the radial direction.
        height = 1.0
        slope = (bot_r - top_r) / height # positive = widens toward base
        for i in range(sectors):
            a0 = 2.0 * math.pi * i / sectors
            a1 = 2.0 * math.pi * (i + 1) / sectors

            def side_vert(angle, y):
                r = bot_r + (top_r - bot_r) * y #lerp from bot_r to top_r
                x = r * math.cos(angle)
                z = r * math.sin(angle)
                #slant normal: outward radial component + upward Y component from slope

                nx = math.cos(angle)
                nz = math.sin(angle)
                ny = slope
                ln = math.sqrt(nx*nx + ny*ny + nz*nz)
                return [x, y, z, nx/ln, ny/ln, nz/ln, angle / (2*math.pi), y]
            
            p00 = side_vert(a0, 0.0)
            p10 = side_vert(a1, 0.0)
            p01 = side_vert(a0, 1.0)
            p11 = side_vert(a1, 1.0)
            verts += p00 + p10 + p11
            verts += p00 + p11 + p01

        arr = np.array(verts, dtype=np.float32)
        self._tapered_cyl = _setup_vao(arr)
        self._tapered_sectors = sectors

    def draw_tapered_cylinder_mesh(self, draw_top=True, draw_bottom=True, draw_sides=True):
        '''
        Draw the tapered cylinder mesh.

        ARGS:
        draw_top............Render the top cap
        draw_bottom.........Render the bottom cap
        draw_sides..........Render the sides
        '''
        if self._tapered_cyl is None:
            return
        
        sectors = getattr(self, '_tapered_sectors', 36)
        glBindVertexArray(self._tapered_cyl["vao"])

        #Bottom cap occupies first sectors*3 vertices
        if draw_bottom:
            glDrawArrays(GL_TRIANGLES, 0, sectors * 3)
        #Top cap follows the bottom cap
        if draw_top:
            glDrawArrays(GL_TRIANGLES, sectors * 3, sectors * 3)
        #Side wall: 6 vertices per sector quad
        if draw_sides:
            glDrawArrays(GL_TRIANGLES, sectors * 6, sectors * 6)

        glBindVertexArray(0)