# *****CODE INFORMATION*****
# Name: Michael King
# Date: 7/17/2026
# File: scene_manager.py
# Assignment: CS-499 Enhancement 1
# CS-330 3D Scene Python Port
# University: SNHU

# Python Port of SceneManager.h/SceneManager.cpp from CS-330 (C++/OpenGL).
# ORIGINALLY MADE BY: Brian Battersby (SNHU Instructor).
# MODIFIED BY: Michael King
# Adapted for CS-499 Software Engineering Enhancement by Michael King
# PORTED TO PYTHON/PyOpenGL BY: Michael King

# The SceneManager class handles:
# - Loading texture images from disk and uploading them to OpenGL texture slots
# - Defining per-object Phong material properties
# - Setting per-draw-call shader uniforms (model transform, texture, material)
# - Orchestrating the rendering of all 7 scene objects:

# OBJECTS:
# ----------------------------------------------------------------------
#   |    OBJECT     |      SHAPE      |   TEXTURE    |     MATERIAL    |
# --|---------------|-----------------|--------------|-----------------|
# 1 | Table Surface | Plane           | wood texture | woodMaterial    |
# 2 | Cutting Board | Box             | yellow_wood  | boardMaterial   |
# 3 | Mug Body      | Cylinder        | ceramic      | ceramicMaterial |
# 4 | Mug Handle    | Torus           | fabric       | fabricMaterial  |
# 5 | Ramekin Bowl  | TaperedCylinder | clay         | clayMaterial    |
# 6 | Fork          | Box             | metal        | metalMaterial   |
# 7 | Knife         | Box             | metal        | metalMaterial   |

# Key Differences from C++:
# - TEXTURE_INFO struct replaced with a list of dicts
# - OBJECT_MATERIAL struct replaced with a list of dicts
# - glm::vec3 arithmetic replaced with pyrr/numpy
# - stb_image.h replaced with Pillow (PIL.Image)

# *** Python Imports ***
import os
import numpy as np
import pyrr
from PIL import Image

from OpenGL.GL import (
    glGenTextures, glBindTexture, glTexParameteri, glTexImage2D,
    glGenerateMipmap, glActiveTexture,
    GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T,
    GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER,
    GL_REPEAT, GL_LINEAR, GL_LINEAR_MIPMAP_LINEAR,
    GL_RGB, GL_RGBA, GL_UNSIGNED_BYTE, GL_TEXTURE0,
)

from shader_manager import ShaderManager
from shape_meshes import ShapeMeshes


class SceneManager:
    '''
    Prepares and renders the 3D Kitchen Scene.

    Mirrors SceneManager.h / SceneManager.cpp from CS-330.
    All texture loading, material definition, and object rendering is
    contained in this class.
    '''

    def __init__(self, shader_manager: ShaderManager, texture_dir: str = "."):
        '''
        Initialize the scene manager.

        ARGS:
        shader_manager......Active ShaderManager instance.
                            Receives all uniform uploads during prepare and render.
        texture_dir.........Directory containing the .jpg texture files.
                            Defaults to the current working directory. 
        '''
        self._shader  = shader_manager
        self._meshes  = ShapeMeshes()
        self._tex_dir = texture_dir

        # List of {'tag': str, 'id': int}; mirrors m_textureIDs[] in C++
        self._textures: list[dict] = []

        # List of material property dicts; mirrors m_objectMaterials in C++
        self._materials: list[dict] = []

    #****************************************************************************
    # Texture Management; mirrors CreateGLTexture / BindGLTextures
    #****************************************************************************

    def _load_texture(self, filename: str, tag: str) -> bool:
        '''
        Load a JPEG/PNG image from disk and upload it to an OpenGL texture slot

        Mirrors SceneManager::CreateGLTexture() + BindGLTextures().
        Uses Pillow (PIL) instead of stb_image.h.

        The image is flipped vertically before upload to match OpenGL's
        bottom left UV origin convention (stbi_set_flip_vertically_on_load(true)).

        ARGS:
        filename....Image filename, relative to self._tex_dir.
        tag.........short string identifier for later lookup (e.g., ceramic).

        Returns true of the texture loaded successfully, false otherwise.
        '''
        path = os.path.join(self._tex_dir, filename)
        try:
            img = Image.open(path).transpose(Image.FLIP_TOP_BOTTOM)
        except FileNotFoundError:
            # Prints error message if image fails to load
            print(f"Could not load image: {path}")
            return False
        
        #Convert to RGB or RGBA so there are 3/4 channels
        if img.mode == "RGB":
            fmt = GL_RGB
        else:
            img = img.convert("RGBA")
            fmt = GL_RGBA

        raw = img.tobytes()
        w, h = img.size

        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)

        # *** WRAPPING ***
        # GL_REPEAT matches glTexParameteri in the C++ version
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        # *** FILTERING ***
        # linear min (with mipmap) and mag filter
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, fmt, w, h, 0, fmt, GL_UNSIGNED_BYTE, raw)
        glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)
        self._textures.append({"tag": tag, "id": tex_id})
        # Prints message if image is successfully loaded
        print(f"Successfully loaded image: {filename}, {w}x{h}, mode={img.mode}")
        return True
    
    def _bind_textures(self):
        '''
        Bind all loaded textures to their sequential GPU texture units.

        Mirrors SceneManager::BindGLTextures().
        Each texture is bound to GL_Texture0 + index so that its sampler unit
        matches FindTextureSlot().
        '''
        for i, tex in enumerate(self._textures):
            glActiveTexture(GL_TEXTURE0 + i)
            glBindTexture(GL_TEXTURE_2D, tex["id"])

    def _find_texture_slot(self, tag: str) -> int:
        '''
        Return the texture unit index (slot) for the given tag.

        Mirrors FindTextureSlot() in SceneManager.cpp.
        Returns -1 if the tag is not found
        '''
        for i, tex in enumerate(self._textures):
            if tex["tag"] == tag:
                return i
        return -1
    
    #****************************************************************************
    # Material Management; mirrors FindMaterial / m_objectMaterials
    #****************************************************************************

    def _find_material(self, tag: str) -> dict | None:
        '''
        Return the material dict associated with the given tag, or None.

        Mirrors SceneManager::FindMaterial().
        '''
        for mat in self._materials:
            if mat["tag"] == tag:
                return mat
        return None
    
    #****************************************************************************
    # Per-draw-call shader helpers
    #****************************************************************************

    def _set_transform(self, scale, rot_x, rot_y, rot_z, pos):
        '''
        Build and upload the model matrix for the next draw call.

        Mirrors SceneManager::SetTransformations().
        The matrix is composed as T * Rx * Ry * Rz * S.
        Translation is last so the object is rotated and scaled in
        object spaced before being placed in the world.

        ARGS:
        scale (tuple)......(sx, sy, sz) uniform scale per axis.
        rot_x (float)......X-axis rotation in degrees.
        rot_y (float)......Y-axis rotation in degrees.
        rot_z (float)......Z-axis rotation in degrees.
        pos   (tuple)......(tx, ty, tz) translation.
        '''
        S  = pyrr.matrix44.create_from_scale(scale,                  dtype=np.float32)
        Rx = pyrr.matrix44.create_from_x_rotation(np.radians(rot_x), dtype=np.float32)
        Ry = pyrr.matrix44.create_from_y_rotation(np.radians(rot_y), dtype=np.float32)
        Rz = pyrr.matrix44.create_from_z_rotation(np.radians(rot_z), dtype=np.float32)
        T = pyrr.matrix44.create_from_translation(pos,               dtype=np.float32)

        #Apply transformations in the same order as the C++ code:
        #translation * rotX * rotY * rotZ * scale
        model = pyrr.matrix44.multiply(
            S, pyrr.matrix44.multiply(
                Rz, pyrr.matrix44.multiply(
                    Ry, pyrr.matrix44.multiply(Rx, T)
                )
            )
        )
        self._shader.set_mat4("model", model)

    def _set_texture(self, tag: str):
        '''
        Tell the shader to sample the texture with the given tag.
        
        Mirrors SceneManager::SetShaderTexture().
        Sets bUseTexture=true and objectTexture=slot.
        '''
        self._shader.set_bool("bUseTexture", True)
        slot = self._find_texture_slot(tag)
        self._shader.set_sampler2d("objectTexture", slot)

    def _set_uv_scale(self, u: float, v: float):
        '''
        set the UV tiling multiplier for the next draw call.

        Mirrors SceneManager::SetTextureUVScale()
        '''
        self._shader.set_vec2("UVscale", u, v)

    def _set_material(self, tag: str):
        '''
        Upload Phong material properties to the shader.
        
        Mirrors SceneManager::SetShaderMaterial();
        '''
        mat = self._find_material(tag)
        if mat is None:
            return
        self._shader.set_vec3("material.ambientColor", *mat["ambient_color"])
        self._shader.set_float("material.ambientStrength", mat["ambient_strength"])
        self._shader.set_vec3("material.diffuseColor", *mat["diffuse_color"])
        self._shader.set_vec3("material.specularColor", *mat["specular_color"])
        self._shader.set_float("material.shininess", mat["shininess"])

    #****************************************************************************
    # Scene setup; mirrors PrepareScene
    #****************************************************************************

    def prepare_scene(self):
        '''
        Load all meshes, textures, and materials into CPU/GPU memory.

        Mirrors SceneManager::PrepareScene() from SceneManager.cpp
        Must be called once after the OpenGL context is active.
        '''
        # *** Load all mesh types used by the scene ***
        self._meshes.load_plane_mesh()
        self._meshes.load_cylinder_mesh()
        self._meshes.load_tapered_cylinder_mesh()
        self._meshes.load_torus_mesh()
        self._meshes.load_box_mesh()

        # *** Load textures into sequential GPU slots ***

        # *** Slot 0 ***
        # Ceramic/smooth white surface for the mug body (cylinder)
        self._load_texture("ceramic.jpg", "ceramic")

        # *** Slot 1 ***
        # Fabric / woven texture for the mug handle (torus)
        # Using a different texture here distinguishes the handle from the body.
        self._load_texture("fabric.jpg", "fabric")

        # *** Slot 2 ***
        # Wood grain texture for the table surface (plane)
        # Will be tiled 4x4 in RenderScene() to avoid a stretched look.
        self._load_texture("wood.jpg", "wood")

        # *** Slot 3 ***
        # Brushed stainless steel for the fork and knife (box shapes)
        self._load_texture("metal.jpg", "metal")

        # *** Slot 4 ***
        # Terra cotta / clay texture for the ramekin bowl (tapered cylinder)
        self._load_texture("clay.jpg", "clay")

        # *** Slot 5 ***
        # Yellow painted wood texture for the cutting board (box shape)
        self._load_texture("yellow_wood.jpg", "yellow_wood")

        # After all textures are loaded into CPU memory, bind them
        # into their corresponding OpenGL texture slots (0-15).
        self._bind_textures()

        #*****************************************************************
        # Define Phong materials.
        # Each dict mirrors an OBJECT_MATERIAL struct from
        # SceneManager.h:
        # 
        # ambient_strength......baseline brightness even in shadow
        # ambient_color.........tint of the ambient bounce light
        # diffuse_color.........main lit color (usually white/neutral)
        # specular_color........highlight color
        # shininess.............higher = tighter, sharper highlight
        #*****************************************************************

        # *** Wood Table Surface ***
        # Varnished finish with visible sheen
        self._materials.append({                  # loads texture material
            "tag":              "woodMaterial",   # tagged as "wood material"
            "ambient_strength": 0.15,             # low ambient light
            "ambient_color":    (0.4, 0.3, 0.2),  # warm brown tint
            "diffuse_color":    (1.0, 1.0, 1.0),  # neutral white diffuse
            "specular_color":   (0.1, 0.1, 0.1),  # warm visible highlight
            "shininess":        4.0,              # very wide, tighter sheen
        })

        # *** Ceramic Mug Body ***
        # Smooth surface, moderate specular highlight
        self._materials.append({                    # loads texture material
            "tag":              "ceramicMaterial",  # tagged as "ceramic material"
            "ambient_strength": 0.2,                # low ambient strength
            "ambient_color":    (0.6, 0.6, 0.7),    # warm dark tint
            "diffuse_color":    (1.0, 1.0, 1.0),    # neutral diffuse
            "specular_color":   (0.5, 0.5, 0.5),    # visible highlight
            "shininess":        32.0,               # medium-tight highlight
        })

        # *** Fabric Mug Handle ***
        # Soft Woven Surface, almost no specular
        self._materials.append({                    # loads texture material
            "tag":              "fabricMaterial",   # tagged as "fabric material"
            "ambient_strength": 0.2,                # low ambient strength
            "ambient_color":    (0.3, 0.25, 0.2),   # warm dark tint
            "diffuse_color":    (1.0, 1.0, 1.0),    # neutral diffuse
            "specular_color":   (0.05, 0.05, 0.05), # nearly no highlight
            "shininess":        2.0,                # low highlight
        })

        # *** Metal Utensils (Fork and Knife) ***
        # Polished Stainless, sharp bright highlight
        self._materials.append({                    # loads texture material
            "tag":              "metalMaterial",    # tagged as "metal material"
            "ambient_strength": 0.15,               # low ambient strength
            "ambient_color":    (0.5, 0.5, 0.5),    # warm bright tint
            "diffuse_color":    (0.9, 0.9, 0.9),    # neutral diffuse
            "specular_color":   (1.0, 1.0, 1.0),    # bright white
            "shininess":        64.0,               # tight glint
        })

	    # *** Clay Ramekin Bowl ***
	    # Unglazed terra cotta, slightly warm, low sheen
        self._materials.append({                    # loads texture material
            "tag":              "clayMaterial",     # tagged as "clay material"
            "ambient_strength": 0.2,                # low ambient strength
            "ambient_color":    (0.5, 0.3, 0.2),    # earthy orange
            "diffuse_color":    (1.0, 1.0, 1.0),    # neutral diffuse
            "specular_color":   (0.2, 0.15, 0.1),   # warm low spec
            "shininess":        8.0,                # low shininess
        })

        # *** Cutting Board***
        # Painted yellow wood, matte finish
        self._materials.append({                    # loads texture material
            "tag":              "boardMaterial",    # tagged as "board material"
            "ambient_strength": 0.25,               # medium ambient strength
            "ambient_color":    (0.5, 0.45, 0.1),   # warm yellow
            "diffuse_color":    (1.0, 1.0, 1.0),    # neutral diffuse
            "specular_color":   (0.1, 0.1, 0.05),   # barely any
            "shininess":        4.0,                # very low shininess
        })

    #****************************************************************************
    # Scene Rendering; mirrors RenderScene
    #****************************************************************************

    def render_scene(self):
        '''
        Set lighting uniforms and draw all 7 scene objects with Phong shading.

        Mirrors SceneManager::RenderScene() from SceneManager.cpp
        Called once per frame from the main render loop.

        --- Scene Objects (matching the image) ---
        1. Table Plane............Large flat surface (Plane)
        2. Cutting Board..........Yellow wooden board (Box)
        3. Coffee Mug Body........Cylinder
        4. Coffee Mug Handle......Torus (complex object with #3)
        5. Ramekin Bowl...........Small brown bowl (Tapered Cylinder)
        6. Fork...................Elongated flat box (Box)
        7. Knife..................Thin elongated box (Box)
  
        --- Lighting ---
        lightSources[0]...........Key Light (warm white, overhead)
        lightSources[1]...........Fill Light (cool blue-white, left-back)

        All objects use full Phong shading:
           Ambient, Diffuse, Specular
        '''
        # Enable lighting calculations in the fragment shader.
        # When false, objects render as flat-textured with no shading.
        self._shader.set_bool("bUseLighting", True)

        #******************************************************************
        # --- LIGHT 0: KEY LIGHT ---
        # Warm white overhead lamp simulating a ceiling light or window.
        # Positioned above and in front of the scene so light falls
        # naturally downward onto the table and the top of the mug.
        # Uses a point light contribution with high focal strength to
        # produce a tight, bright specular highlight on the ceramic mug.
        #******************************************************************

        # Above and in front of the scene so light falls naturally
        # downward onto the table and mug top
        self._shader.set_vec3("lightSources[0].position", 3.0, 8.0, 4.0)

        # Low ambient keeps unlit areas slightly visible without
        # washing out the contrast created by the key light
        self._shader.set_vec3("lightSources[0].ambientColor", 0.2, 0.2, 0.2)

        # Warm white (slightly reduced blue) mimics incandescent or
        # late-afternoon sunlight color temperature
        self._shader.set_vec3("lightSources[0].diffuseColor", 1.0, 0.95, 0.8)

        # Near-white specular produces a bright, clean highlight on
        # the smooth ceramic mug surface
        self._shader.set_vec3("lightSources[0].specularColor", 1.0, 1.0, 0.9)

   	    # High focal strength (32) tightens the specular cone,
	    # giving the ceramic a sharp, glossy-looking highlight     
        self._shader.set_float("lightSources[0].focalStrength", 32.0)
        
        # Strong specular intensity (0.8) makes the highlight clearly
        # visible on the mug body to demonstrate light reflection
        self._shader.set_float("lightSources[0].specularIntensity", 0.8)

        #***********************************************************************
	    # --- LIGHT 1: FILL LIGHT (colored) ---
	    # Cool blue-tinted light from the left side and slightly behind.
	    # Prevents the back face of the mug from falling into full shadow.
	    # A fill light is standard in three-point lighting.
	    # The cool color contrasts with the warm key light and adds visual depth.
	    # This light is distinctly colored (blue-white).
	    #***********************************************************************

        # Left side and slightly behind so it lights the back face of the
	    # mug that the key light cannot reach directly
        self._shader.set_vec3("lightSources[1].position", -5.0, 4.0, -2.0)

        # Very low ambient
        # the fill light's job is to lift shadows,
        # not to add a second strong ambient source.
        self._shader.set_vec3("lightSources[1].ambientColor", 0.1, 0.1, 0.15)

        # Cool blue-white diffuse (sky bounce light)
        # contrasts with the warm key light and adds visual depth to the scene
        self._shader.set_vec3("lightSources[1].diffuseColor", 0.5, 0.55, 0.7)

	    # Muted cool specular
	    # the full should not produce a competing highlight
	    # just a soft sheen on back-facing surfaces
        self._shader.set_vec3("lightSources[1].specularColor", 0.3, 0.3, 0.5)

        # Low focal strength (8)
        # spreads the specular broadly, keeping the fill contribution
        # soft and non-distracting
        self._shader.set_float("lightSources[1].focalStrength", 8.0)

        # Low specular intensity (0.2)
        # ensures the fill light only subtly brightens shadow areas without
        # overpowering the key
        self._shader.set_float("lightSources[1].specularIntensity", 0.2)


        #*********************************************************************
	    # --- OBJECT 1: TABLE SURFACE (Plane) ---
	    # A large flat plane representing the kitchen countertop.
	    # Scaled wide (x = 20) and deep (z = 10) and very thin in Y.
	    # Placed at the origin (y = 0) as the ground level for the scene.
	    # Wood grain texture tiled 4x4 prevents a stretched appearance
	    # on the large surface; this is the complex UV technique.
    	#********************************************************************/
	
        self._set_transform(
            scale=(20.0, 1.0, 10.0), #scale: flat ground plane
            rot_x=0.0, rot_y=0.0, rot_z=0.0, #No Rotation required for this plane
            pos=(0.0, 0.0, 0.0),) #at origin
        self._set_texture("wood") #Select wood texture for this plane
        
        #Tile the texture 4 times in U and 4 times in V so the wood grain
        #does not appear stretched across the large plane surface
        self._set_uv_scale(4.0, 4.0)
        self._set_material("woodMaterial") # apply wood material
        self._meshes.draw_plane_mesh() #Draws Mesh for the plane
	
	    #************************************************************************
	    # --- OBJECT 2: CUTTING BOARD (BOX) ---
	    # A yellow painted wooden cutting board sitting on the countertop.
	    # Matches the prominent yellow surface in the image.
	    # Scale...........wide, deep and thin (like a real cutting board)
	    # Position........centered on the table, slightly above the plane
	    #************************************************************************/
	
        self._set_transform(
            scale=(7.0, 0.15, 3.5), # wide, deep, thin board
            rot_x=0.0, rot_y=0.0, rot_z=0.0, # no rotation required
            pos=(0.0, 0.08, 0.5),) # centered, just above the plane
        self._set_texture("yellow_wood") # select yellow wood texture for the cutting board
        self._set_uv_scale(1.0, 1.0) # 1x1 scale maps the image around the cutting board without tiling
        self._set_material("boardMaterial") # apply board material
        self._meshes.draw_box_mesh() # Draws Box for the cutting board

	    #************************************************************************
	    # --- OBJECT 3: MUG BODY (Cylinder) ---
	    # Represents the main body of the coffee mug.
	    # A real mug is taller than it is wide, so Y is scaled up.
	    # Placed at the center-right area of the board.
	    # Ceramic texture wraps once around (UV 1x1) for a clean look.
	    # This is one half of the complex mug object (with the torus).
	    #************************************************************************/

        self._set_transform(
            scale=(0.85, 2.0, 0.85), #Radius-like x/z, height y
            rot_x=0.0, rot_y=0.0, rot_z=0.0, #No Rotation required for this shape
            pos=(-0.3, 0.16, 0.2),) #on top of the cutting board
        self._set_texture("ceramic") #Select the ceramic texture for the mug body
        self._set_uv_scale(1.0, 1.0) # 1x1 scale maps the image once around the cylinder without tiling
        self._set_material("ceramicMaterial") # apply ceramic material
        self._meshes.draw_cylinder_mesh() #Draws Mesh for the Cylinder

        #**************************************************************************
        # --- OBJECT 4: MUG HANDLE (Torus) ---
        # Represents the handle of the coffee mug.
        # A torus is a donut shape, which is perfect for a mug handle.
        # Positioned flush against the cylinder wall (x = 0.6 from mug)
        # and centered on the mug's height (y = 1.16 = 0.16 base + 1.0).
        # Uses a fabric/woven texture, different from the ceramic body.
        # 
        # A 2x2 scale repeats the weave twice around the ring so the
        # fabric detail appears at the right density for the handle's size.
        #**************************************************************************/

        self._set_transform(
            scale=(1.0, 1.0, 1.0), # small and thin like a real handle
            rot_x=90.0, rot_y=0.0, rot_z=0.0, #90 Degree X rotation
            pos=(0.6, 1.16, 0.3),) #Flush to cylinder wall, centered on mug height
        self._set_texture("fabric") #Select the fabric texture for the mug handle
        
        # 2x2 tiling keeps the weave pattern fine enough to look realistic
        # on a small handle rather than a single oversized tile.
        self._set_uv_scale(2.0, 2.0)
        self._set_material("fabricMaterial") #apply fabric material
        self._meshes.draw_torus_mesh() #Draw Mesh for the torus

        #***************************************************************************
        # --- OBJECT 5: RAMEKIN BOWL (Tapered Cylinder) ---
        # A small brown clay/terra cotta ramekin bowl.
        # Matches the small brown bowl to the right of the mug in the image.
        # A tapered cylinder is wider at the top than the bottom,
        # which naturally approximates a ramekin or small bowl shape.
        # Flipped 180 degrees (X) so it looks like a real ramekin bowl.
        #***************************************************************************/
        
        self._set_transform(
            scale=(0.7, 0.6, 0.7),   #small radius, short height
            rot_x=180.0, rot_y=0.0, rot_z=0.0, #180 degree X rotation
            pos=(1.8, 0.76, 0.2),) #to the right of the mug, on board
        self._set_texture("clay") #Select clay texture for bowl
        self._set_uv_scale(1.0, 1.0) #1x1 scale wraps texture once around the ramekin bowl
        self._set_material("clayMaterial") #apply clay material
        self._meshes.draw_tapered_cylinder_mesh() #Draw Tapered Cylinder for the bowl

        #******************************************************************************
        # --- OBJECT 6: FORK (Box) ---
        # A flat elongated box approximating a dinner fork.
        # Laid flat on the cutting board, rotated slightly to match the
        # diagonal angle visible in the reference photo.
        # Scale: very long (Z), narrow (X), and very thin (Y).
        # Metal texture with high specular gives a stainless steel look.
        #******************************************************************************/

        self._set_transform(
            scale=(0.22, 0.07, 2.4),  #long, narrow, flat for visibility
            rot_x=0.0, rot_y=10.0, rot_z=0.0,  #slight Y rotation
            pos=(-2.0, 0.2, 0.3)) #left side of the cutting board
        self._set_texture("metal")  #select metal texture for the fork
        self._set_uv_scale(1.0, 6.0) #tile along length for steel grain effect
        self._set_material("metalMaterial") #apply metal material
        self._meshes.draw_box_mesh()  #Draw Box for the fork

        #******************************************************************************
        # --- OBJECT 7: KNIFE (Box) ---
        # A thin elongated box approximating a dinner knife.
        # Placed parallel to the form, slightly to its right.
        # Scale: very long (Z), narrow (X), extremely thin (Y).
        # Same metal texture as the fork for visual consistency.
        #******************************************************************************/

        self._set_transform(
            scale=(0.14, 0.07, 2.4),  #long, narrow, very thin blade
            rot_x=0.0, rot_y=10.0, rot_z=0.0,  #slight Y rotation
            pos=(-1.5, 0.2, 0.3)) #just right of the fork
        self._set_texture("metal") #select metal texture for the knife
        self._set_uv_scale(1.0, 6.0)  #tile along length for steel grain effect
        self._set_material("metalMaterial") #apply metal material
        self._meshes.draw_box_mesh()  #Draw Box for the Knife
