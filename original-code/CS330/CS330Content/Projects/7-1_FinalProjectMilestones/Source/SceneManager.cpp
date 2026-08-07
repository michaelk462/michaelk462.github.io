///////////////////////////////////////////////////////////////////////////////
// shadermanager.cpp
// ============
// manage the loading and rendering of 3D scenes
//
//  AUTHOR: Brian Battersby - SNHU Instructor / Computer Science
//	Created for CS-330-Computational Graphics and Visualization, Nov. 1st, 2023
// 
// MODIFIED BY: Michael King
// *************************************
// *         MILESTONE TWO             *
// *************************************
// CHANGES MADE:
// - Built a complex object (coffee mug) using two primitive shapes:
//   Cylinder....................Mug Body
//   Torus.......................Mug Handle
// 
// *************************************
// *         MILESTONE THREE           *
// *************************************
// CHANGE MADE:
// - Added a 3D Plane as a base/table for all objects.
// 
// *************************************
// *         MILESTONE FOUR            *
// *************************************
// CHANGES MADE:
// - Loaded three textures in PrepareScene() using CreateGLTexture():
//   "ceramic"................Mug Body (cylinder)
//   "fabric".................Mug Handle (torus)
//   "wood"...................Table Surface (wood)
// - Replaced all SetShaderColor() calls in RenderScene() with
//   SetShaderTexture() + SetTextureUVScale() calls
// - Added BindGLTextures() call at the top of RenderScene() so all
//   loaded textures are active in their GPU slots before drawing
// - Applied UV tiling on the plane (4x4) to ensure complex texturing
//   technique
// - Cylinder and torus use different textures on the same complex
//   object
// 
// *************************************
// *         MILESTONE FIVE            *
// *************************************
// CHANGES MADE:
// - Defined three OBJECT_MATERIAL structs in PrepareScene():
//   "woodMaterial"............Table Plane  (matte, low specular)
//   "ceramicMaterial".........Mug Body     (moderate specular, shininess 32)
//   "fabricMaterial"..........Mug Handle   (near-zero specular, soft)
// - Enabled bUseLighting in RenderScene() to activate Phong shading
// - Added two light sources to RenderScene():
//   lightSources[0]...........Key Light  (warm white, overhead)
//   lightSources[1]...........Fill Light (cool blue-white, left/back)
// - Called SetShaderMaterial() before each draw call so each surface
//   responds to light according to its physical properties
// 
// *************************************
// *          FINAL PROJECT            *
// *************************************
// - Added four additional objects to the 3D scene to meet the
//   requirement of at least four completed objects:
//   1. Cutting Board..........Box (yellow wooden board, center of scene)
//   2. Fork...................Box (flat elongated shape, left of board)
//   3. Knife..................Box (thin elongated shape, right of board)
//   4. Ramekin Bowl...........Tapered Cylinder (small brown bowl, right of mug)
// - Added new textures:
//   "metal"...................Stainless steel for fork and knife
//   "clay"....................Terra cotta / clay for ramekin
//   "yellow_wood".............Painted wood surface for the cutting board
// - Added new materials: metalMaterial, clayMaterial, boardMaterial
// - Loaded additional meshes: BoxMesh, SphereMesh
// - Scene now contains all required shape types:
//   Plane, Cylinder, Torus, Box, Tapered Cylinder
///////////////////////////////////////////////////////////////////////////////

#include "SceneManager.h"

#ifndef STB_IMAGE_IMPLEMENTATION
#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#endif

#include <glm/gtx/transform.hpp>

// declaration of global variables
namespace
{
	const char* g_ModelName = "model";
	const char* g_ColorValueName = "objectColor";
	const char* g_TextureValueName = "objectTexture";
	const char* g_UseTextureName = "bUseTexture";
	const char* g_UseLightingName = "bUseLighting";
}

/***********************************************************
 *  SceneManager()
 *
 *  The constructor for the class
 ***********************************************************/
SceneManager::SceneManager(ShaderManager *pShaderManager)
{
	m_pShaderManager = pShaderManager;
	m_basicMeshes = new ShapeMeshes();
}

/***********************************************************
 *  ~SceneManager()
 *
 *  The destructor for the class
 ***********************************************************/
SceneManager::~SceneManager()
{
	m_pShaderManager = NULL;
	delete m_basicMeshes;
	m_basicMeshes = NULL;
}

/***********************************************************
 *  CreateGLTexture()
 *
 *  This method is used for loading textures from image files,
 *  configuring the texture mapping parameters in OpenGL,
 *  generating the mipmaps, and loading the read texture into
 *  the next available texture slot in memory.
 ***********************************************************/
bool SceneManager::CreateGLTexture(const char* filename, std::string tag)
{
	int width = 0;
	int height = 0;
	int colorChannels = 0;
	GLuint textureID = 0;

	// indicate to always flip images vertically when loaded
	stbi_set_flip_vertically_on_load(true);

	// try to parse the image data from the specified image file
	unsigned char* image = stbi_load(
		filename,
		&width,
		&height,
		&colorChannels,
		0);

	// if the image was successfully read from the image file
	if (image)
	{
		std::cout << "Successfully loaded image:" << filename << ", width:" << width << ", height:" << height << ", channels:" << colorChannels << std::endl;

		glGenTextures(1, &textureID);
		glBindTexture(GL_TEXTURE_2D, textureID);

		// set the texture wrapping parameters
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
		// set texture filtering parameters
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

		// if the loaded image is in RGB format
		if (colorChannels == 3)
			glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB8, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, image);
		// if the loaded image is in RGBA format - it supports transparency
		else if (colorChannels == 4)
			glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image);
		else
		{
			std::cout << "Not implemented to handle image with " << colorChannels << " channels" << std::endl;
			return false;
		}

		// generate the texture mipmaps for mapping textures to lower resolutions
		glGenerateMipmap(GL_TEXTURE_2D);

		// free the image data from local memory
		stbi_image_free(image);
		glBindTexture(GL_TEXTURE_2D, 0); // Unbind the texture

		// register the loaded texture and associate it with the special tag string
		m_textureIDs[m_loadedTextures].ID = textureID;
		m_textureIDs[m_loadedTextures].tag = tag;
		m_loadedTextures++;

		return true;
	}

	std::cout << "Could not load image:" << filename << std::endl;

	// Error loading the image
	return false;
}

/***********************************************************
 *  BindGLTextures()
 *
 *  This method is used for binding the loaded textures to
 *  OpenGL texture memory slots.  There are up to 16 slots.
 ***********************************************************/
void SceneManager::BindGLTextures()
{
	for (int i = 0; i < m_loadedTextures; i++)
	{
		// bind textures on corresponding texture units
		glActiveTexture(GL_TEXTURE0 + i);
		glBindTexture(GL_TEXTURE_2D, m_textureIDs[i].ID);
	}
}

/***********************************************************
 *  DestroyGLTextures()
 *
 *  This method is used for freeing the memory in all the
 *  used texture memory slots.
 ***********************************************************/
void SceneManager::DestroyGLTextures()
{
	for (int i = 0; i < m_loadedTextures; i++)
	{
		glGenTextures(1, &m_textureIDs[i].ID);
	}
}

/***********************************************************
 *  FindTextureID()
 *
 *  This method is used for getting an ID for the previously
 *  loaded texture bitmap associated with the passed in tag.
 ***********************************************************/
int SceneManager::FindTextureID(std::string tag)
{
	int textureID = -1;
	int index = 0;
	bool bFound = false;

	while ((index < m_loadedTextures) && (bFound == false))
	{
		if (m_textureIDs[index].tag.compare(tag) == 0)
		{
			textureID = m_textureIDs[index].ID;
			bFound = true;
		}
		else
			index++;
	}

	return(textureID);
}

/***********************************************************
 *  FindTextureSlot()
 *
 *  This method is used for getting a slot index for the previously
 *  loaded texture bitmap associated with the passed in tag.
 ***********************************************************/
int SceneManager::FindTextureSlot(std::string tag)
{
	int textureSlot = -1;
	int index = 0;
	bool bFound = false;

	while ((index < m_loadedTextures) && (bFound == false))
	{
		if (m_textureIDs[index].tag.compare(tag) == 0)
		{
			textureSlot = index;
			bFound = true;
		}
		else
			index++;
	}

	return(textureSlot);
}

/***********************************************************
 *  FindMaterial()
 *
 *  This method is used for getting a material from the previously
 *  defined materials list that is associated with the passed in tag.
 ***********************************************************/
bool SceneManager::FindMaterial(std::string tag, OBJECT_MATERIAL& material)
{
	if (m_objectMaterials.size() == 0)
	{
		return(false);
	}

	int index = 0;
	bool bFound = false;
	while ((index < m_objectMaterials.size()) && (bFound == false))
	{
		if (m_objectMaterials[index].tag.compare(tag) == 0)
		{
			bFound = true;
			material.ambientColor = m_objectMaterials[index].ambientColor;
			material.ambientStrength = m_objectMaterials[index].ambientStrength;
			material.diffuseColor = m_objectMaterials[index].diffuseColor;
			material.specularColor = m_objectMaterials[index].specularColor;
			material.shininess = m_objectMaterials[index].shininess;
		}
		else
		{
			index++;
		}
	}

	return(true);
}

/***********************************************************
 *  SetTransformations()
 *
 *  This method is used for setting the transform buffer
 *  using the passed in transformation values.
 ***********************************************************/
void SceneManager::SetTransformations(
	glm::vec3 scaleXYZ,
	float XrotationDegrees,
	float YrotationDegrees,
	float ZrotationDegrees,
	glm::vec3 positionXYZ)
{
	// variables for this method
	glm::mat4 modelView;
	glm::mat4 scale;
	glm::mat4 rotationX;
	glm::mat4 rotationY;
	glm::mat4 rotationZ;
	glm::mat4 translation;

	// set the scale value in the transform buffer
	scale = glm::scale(scaleXYZ);
	// set the rotation values in the transform buffer
	rotationX = glm::rotate(glm::radians(XrotationDegrees), glm::vec3(1.0f, 0.0f, 0.0f));
	rotationY = glm::rotate(glm::radians(YrotationDegrees), glm::vec3(0.0f, 1.0f, 0.0f));
	rotationZ = glm::rotate(glm::radians(ZrotationDegrees), glm::vec3(0.0f, 0.0f, 1.0f));
	// set the translation value in the transform buffer
	translation = glm::translate(positionXYZ);

	modelView = translation * rotationX * rotationY * rotationZ * scale;

	if (NULL != m_pShaderManager)
	{
		m_pShaderManager->setMat4Value(g_ModelName, modelView);
	}
}

/***********************************************************
 *  SetShaderColor()
 *
 *  This method is used for setting the passed in color
 *  into the shader for the next draw command
 ***********************************************************/
void SceneManager::SetShaderColor(
	float redColorValue,
	float greenColorValue,
	float blueColorValue,
	float alphaValue)
{
	// variables for this method
	glm::vec4 currentColor;

	currentColor.r = redColorValue;
	currentColor.g = greenColorValue;
	currentColor.b = blueColorValue;
	currentColor.a = alphaValue;

	if (NULL != m_pShaderManager)
	{
		m_pShaderManager->setIntValue(g_UseTextureName, false);
		m_pShaderManager->setVec4Value(g_ColorValueName, currentColor);
	}
}

/***********************************************************
 *  SetShaderTexture()
 *
 *  This method is used for setting the texture data
 *  associated with the passed in ID into the shader.
 ***********************************************************/
void SceneManager::SetShaderTexture(
	std::string textureTag)
{
	if (NULL != m_pShaderManager)
	{
		m_pShaderManager->setIntValue(g_UseTextureName, true);

		int textureID = -1;
		textureID = FindTextureSlot(textureTag);
		m_pShaderManager->setSampler2DValue(g_TextureValueName, textureID);
	}
}

/***********************************************************
 *  SetTextureUVScale()
 *
 *  This method is used for setting the texture UV scale
 *  values into the shader.
 ***********************************************************/
void SceneManager::SetTextureUVScale(float u, float v)
{
	if (NULL != m_pShaderManager)
	{
		m_pShaderManager->setVec2Value("UVscale", glm::vec2(u, v));
	}
}

/***********************************************************
 *  SetShaderMaterial()
 *
 *  This method is used for passing the material values
 *  into the shader.
 ***********************************************************/
void SceneManager::SetShaderMaterial(
	std::string materialTag)
{
	if (m_objectMaterials.size() > 0)
	{
		OBJECT_MATERIAL material;
		bool bReturn = false;

		bReturn = FindMaterial(materialTag, material);
		if (bReturn == true)
		{
			m_pShaderManager->setVec3Value("material.ambientColor", material.ambientColor);
			m_pShaderManager->setFloatValue("material.ambientStrength", material.ambientStrength);
			m_pShaderManager->setVec3Value("material.diffuseColor", material.diffuseColor);
			m_pShaderManager->setVec3Value("material.specularColor", material.specularColor);
			m_pShaderManager->setFloatValue("material.shininess", material.shininess);
		}
	}
}

/**************************************************************/
/*** STUDENTS CAN MODIFY the code in the methods BELOW for  ***/
/*** preparing and rendering their own 3D replicated scenes.***/
/*** Please refer to the code in the OpenGL sample project  ***/
/*** for assistance.                                        ***/
/**************************************************************/


/***********************************************************
 *  PrepareScene()
 *
 *  This method is used for preparing the 3D scene by loading
 *  the shapes, textures in memory to support the 3D scene 
 *  rendering
 * 
 * --- Meshes Loaded ---
 * Plane................Table surface
 * Cylinder.............Mug body
 * TaperedCylinder......Ramekin bowl
 * Torus................Mug handle
 * Box..................Cutting board, fork knife
 * 
 * --- Textures Loaded (Slot order) ---
 * 0  "ceramic".............White smooth surface (mug body)
 * 1  "fabric"..............Woven texture (mug handle)
 * 2  "wood"................Wood grain (table surface)
 * 3  "metal"...............Brushed steel (fork and knife)
 * 4  "clay"................Terra cotta (ramekin bowl)
 * 5  "yellow_wood".........Painted wood (cutting board)
 * 
 * --- Materials Defined ---
 * woodMaterial..........Matte, low specular (table)
 * ceramicMaterial.......Moderate specular, shininess 32 (mug)
 * fabricMaterial........Very low specular, soft (handle)
 * metalMaterial.........High specular, shininess 64 (utensils)
 * clayMaterial..........Low-moderate specular (ramekin)
 * boardMaterial.........Low specular, warm (cutting board)
 ***********************************************************/
void SceneManager::PrepareScene()
{
	// only one instance of a particular mesh needs to be
	// loaded in memory no matter how many times it is drawn
	// in the rendered 3D scene

	m_basicMeshes->LoadPlaneMesh();
	m_basicMeshes->LoadCylinderMesh();
	m_basicMeshes->LoadTaperedCylinderMesh();
	m_basicMeshes->LoadTorusMesh();
	m_basicMeshes->LoadBoxMesh();

	// --------------------------------------------------------------
	// Load textures using CreateGLTexture(filepath, tag).
	// The tag is a short string used later in SetShaderTexture()
	// to identify which texture to bind before each draw call.
	// Textures are stored in m_textureIDs[] in load order.
	// --------------------------------------------------------------

	// *** Slot 0 ***
	// Ceramic/smooth white surface for the mug body (cylinder)
	CreateGLTexture("ceramic.jpg", "ceramic");

	// *** Slot 1 ***
	// Fabric / woven texture for the mug handle (torus)
	// Using a different texture here distinguishes the handle from the body.
	CreateGLTexture("fabric.jpg", "fabric");

	// *** Slot 2 ***
	// Wood grain texture for the table surface (plane)
	// Will be tiled 4x4 in RenderScene() to avoid a stretched look.
	CreateGLTexture("wood.jpg", "wood");

	// *** Slot 3 ***
	// Brushed stainless steel for the fork and knife (box shapes)
	CreateGLTexture("metal.jpg", "metal");

	// *** Slot 4 ***
	// Terra cotta / clay texture for the ramekin bowl (tapered cylinder)
	CreateGLTexture("clay.jpg", "clay");

	// *** Slot 5 ***
	// Yellow painted wood texture for the cutting board (box shape)
	CreateGLTexture("yellow_wood.jpg", "yellow_wood");

	//After all textures are loaded into CPU memory, bind them
	//into their corresponding OpenGL texture slots (0-15).
	BindGLTextures();

	/*****************************************************************
	* Define object materials.
	* Each material controls how the surface responds to light:
	* 
	* ambienceStrength......baseline brightness even in shadow
	* ambienceColor.........tint of the ambient bounce light
	* diffuseColor..........main lit color (usually white/neutral)
	* specularColor.........highlight color
	* shininess.............higher = tighter, sharper highlight
	*****************************************************************/

	//*** Wood Table Surface ***
	//Varnished finish with visible sheen
	OBJECT_MATERIAL woodMaterial; 
	woodMaterial.ambientStrength = 0.15f;                         // low ambient strength
	woodMaterial.ambientColor    = glm::vec3(0.4f, 0.3f, 0.2f);   // warm brown tint
	woodMaterial.diffuseColor    = glm::vec3(1.0f, 1.0f, 1.0f);   // neutral white diffuse
	woodMaterial.specularColor   = glm::vec3(0.1f, 0.1f, 0.1f);   // warm visible highlight
	woodMaterial.shininess       = 4.0f;                          // very wide, tighter sheen
	woodMaterial.tag             = "woodMaterial";                // tagged as "wood material"
	m_objectMaterials.push_back(woodMaterial);                    // loads texture material

	//*** Ceramic Mug Body ***
	//Smooth surface, moderate specular highlight
	OBJECT_MATERIAL ceramicMaterial;
	ceramicMaterial.ambientStrength = 0.2f;                        // low ambient strength
	ceramicMaterial.ambientColor    = glm::vec3(0.6f, 0.6f, 0.7f); // warm dark tint
	ceramicMaterial.diffuseColor    = glm::vec3(1.0f, 1.0f, 1.0f); // neutral diffuse
	ceramicMaterial.specularColor   = glm::vec3(0.5f, 0.5f, 0.5f); // visible highlight
	ceramicMaterial.shininess       = 32.0f;                       // medium-tight highlight
	ceramicMaterial.tag             = "ceramicMaterial";           // tagged as "ceramic material"
	m_objectMaterials.push_back(ceramicMaterial);                  // loads texture material

	//*** Fabric Mug Handle ***
	//Soft Woven Surface, almost no specular
	OBJECT_MATERIAL fabricMaterial;
	fabricMaterial.ambientStrength = 0.2f;                           //low ambient strength
	fabricMaterial.ambientColor    = glm::vec3(0.3f, 0.25f, 0.2f);   //warm dark tint
	fabricMaterial.diffuseColor    = glm::vec3(1.0f, 1.0f, 1.0f);    //neutral diffuse
	fabricMaterial.specularColor   = glm::vec3(0.05f, 0.05f, 0.05f); //nearly no highlight
	fabricMaterial.shininess       = 2.0f;                           //low highlight
	fabricMaterial.tag             = "fabricMaterial";               //tagged as "fabric material"
	m_objectMaterials.push_back(fabricMaterial);                     //loads texture material

	//*** Metal Utensils (Fork and Knife) ***
	//Polished Stainless, sharp bright highlight
	OBJECT_MATERIAL metalMaterial;
	metalMaterial.ambientStrength = 0.15f;                           //low ambient strength
	metalMaterial.ambientColor    = glm::vec3(0.5f, 0.5f, 0.5f);     //warm bright tint
	metalMaterial.diffuseColor    = glm::vec3(0.9f, 0.9f, 0.9f);     //neutral diffuse
	metalMaterial.specularColor   = glm::vec3(1.0f, 1.0f, 1.0f);     //bright white
	metalMaterial.shininess       = 64.0f;                           //tight glint
	metalMaterial.tag             = "metalMaterial";                 //tagged as "metal material"
	m_objectMaterials.push_back(metalMaterial);                      //loads texture material

	//*** Clay Ramekin Bowl ***
	//Unglazed terra cotta, slightly warm, low sheen
	OBJECT_MATERIAL clayMaterial;
	clayMaterial.ambientStrength = 0.2f;                             //low ambient strength
	clayMaterial.ambientColor    = glm::vec3(0.5f, 0.3f, 0.2f);      //earthy orange
	clayMaterial.diffuseColor    = glm::vec3(1.0f, 1.0f, 1.0f);      //neutral diffuse
	clayMaterial.specularColor   = glm::vec3(0.2f, 0.15f, 0.1f);     //warm low spec
	clayMaterial.shininess       = 8.0f;                             //low shininess
	clayMaterial.tag = "clayMaterial";                               //tagged as "clay material"
	m_objectMaterials.push_back(clayMaterial);                       //loads texture material

	// *** Cutting Board***
	//Painted yellow wood, matte finish
	OBJECT_MATERIAL boardMaterial;
	boardMaterial.ambientStrength = 0.25f;                           //medium ambient strength
	boardMaterial.ambientColor    = glm::vec3(0.5f, 0.45f, 0.1f);    //warm yellow
	boardMaterial.diffuseColor    = glm::vec3(1.0f, 1.0f, 1.0f);     //neutral diffuse
	boardMaterial.specularColor   = glm::vec3(0.1f, 0.1f, 0.05f);    //barely any
	boardMaterial.shininess       = 4.0f;                            //very low shininess
	boardMaterial.tag             = "boardMaterial";                 //tagged as "board material"    
	m_objectMaterials.push_back(boardMaterial);                      //loads texture material
}

/***********************************************************
 *  RenderScene()
 *
 *  This method is used for rendering the 3D scene by 
 *  transforming and drawing the basic 3D shapes
 * 
 *	--- Scene Objects (matching the image) ---
 * 1. Table Plane............Large flat surface (Plane)
 * 2. Cutting Board..........Yellow wooden board (Box)
 * 3. Coffee Mug Body........Cylinder
 * 4. Coffee Mug Handle......Torus (complex object with #3)
 * 5. Ramekin Bowl...........Small brown bowl (Tapered Cylinder)
 * 6. Fork...................Elongated flat box (Box)
 * 7. Knife..................Thin elongated box (Box)
 * 
 *  --- Lighting ---
 * lightSources[0]...........Key Light (warm white, overhead)
 * lightSources[1]...........Fill Light (cool blue-white, left-back)
 * 
 * All objects use full Phong shading:
 *    Ambient, Diffuse, Specular
 ***********************************************************/
void SceneManager::RenderScene()
{
	// Enable lighting calculations in the fragment shader.
	// When false, objects render as flat-textured with no shading.
	m_pShaderManager->setIntValue(g_UseLightingName, true);

	/***************************************************************
	* --- LIGHT O: KEY LIGHT ---
	* Warm white overhead lamp simulating a ceiling light or window.
	* Positioned above and in front of the scene so light falls
	* naturally downward onto the table and the top of the mug.
	* Uses a point light contribution with high focal strength to
	* produce a tight, bright specular highlight on the ceramic mug.
	****************************************************************/

	// Above and in front of the scene so light falls naturally
	// downward onto the table and mug top
	m_pShaderManager->setVec3Value("lightSources[0].position",
		glm::vec3(3.0f, 8.0f, 4.0f));

	// Low ambient keeps unlit areas slightly visible without
	// washing out the contrast created by the key light
	m_pShaderManager->setVec3Value("lightSources[0].ambientColor",
		glm::vec3(0.2f, 0.2f, 0.2f));

	// Warm white (slightly reduced blue) mimics incandescent or
	// late-afternoon sunlight color temperature
	m_pShaderManager->setVec3Value("lightSources[0].diffuseColor",
		glm::vec3(1.0f, 0.95f, 0.8f));

	// Near-white specular produces a bright, clean highlight on
	// the smooth ceramic mug surface
	m_pShaderManager->setVec3Value("lightSources[0].specularColor",
		glm::vec3(1.0f, 1.0f, 0.9f));

	// High focal strength (32) tightens the specular cone,
	// giving the ceramic a sharp, glossy-looking highlight
	m_pShaderManager->setFloatValue("lightSources[0].focalStrength",
		32.0f);

	// Strong specular intensity (1.0) makes the highlight clearly
	// visible on the mug body to demonstrate light reflection
	m_pShaderManager->setFloatValue("lightSources[0].specularIntensity",
		0.8f);

	/***********************************************************************
	* --- LIGHT 1: FILL LIGHT (colored) ---
	* Cool blue-tinted light from the left side and slightly behind.
	* Prevents the back face of the mug from falling into full shadow.
	* A fill light is standard in three-point lighting.
	* The cool color contrasts with the warm key light and adds visual depth.
	* This light is distinctly colored (blue-white).
	***********************************************************************/

	// Left side and slightly behind so it lights the back face of the
	// mug that the key light cannot reach directly
	m_pShaderManager->setVec3Value("lightSources[1].position",
		glm::vec3(-5.0f, 4.0f, -2.0f));

	// Very low ambient
	// the fill light's job is to lift shadows,
	// not to add a second strong ambient source.
	m_pShaderManager->setVec3Value("lightSources[1].ambientColor",
		glm::vec3(0.1f, 0.1f, 0.15f));

	// Cool blue-white diffuse (sky bounce light)
	// contrasts with the warm key light and adds visual depth to the scene
	m_pShaderManager->setVec3Value("lightSources[1].diffuseColor",
		glm::vec3(0.5f, 0.55f, 0.7f));

	// Muted cool specular
	// the full should not produce a competing highlight
	// just a soft sheen on back-facing surfaces
	m_pShaderManager->setVec3Value("lightSources[1].specularColor",
		glm::vec3(0.3f, 0.3f, 0.5f));

	// Low focal strength (8)
	// spreads the specular broadly, keeping the fill contribution
	// soft and non-distracting
	m_pShaderManager->setFloatValue("lightSources[1].focalStrength",
		8.0f);

	// Low specular intensity (0.2)
	// ensures the fill light only subtly brightens shadow areas without
	// overpowering the key
	m_pShaderManager->setFloatValue("lightSources[1].specularIntensity",
		0.2f);

	/*********************************************************************
	* --- OBJECT 1: TABLE SURFACE (Plane) ---
	* A large flat plane representing the kitchen countertop.
	* Scaled wide (x = 20) and deep (z = 10) and very thin in Y.
	* Placed at the origin (y = 0) as the ground level for the scene.
	* Wood grain texture tiled 4x4 prevents a stretched appearance
	* on the large surface; this is the complex UV technique.
	*********************************************************************/
	
	SetTransformations(
		glm::vec3(20.0f, 1.0f, 10.0f), //scale: flat ground plane
		0.0f, 0.0f, 0.0f, //No Rotation required for this plane
		glm::vec3(0.0f, 0.0f, 0.0f)); //at origin
	SetShaderTexture("wood"); //Select wood texture for this plane
	
	//Tile the texture 4 times in U and 4 times in V so the wood grain
	//does not appear stretched across the large plane surface
	SetTextureUVScale(4.0f, 4.0f);
	SetShaderMaterial("woodMaterial"); // apply wood material
	m_basicMeshes->DrawPlaneMesh(); //Draws Mesh for the plane
	
	/************************************************************************
	* --- OBJECT 2: CUTTING BOARD (BOX) ---
	* A yellow painted wooden cutting board sitting on the countertop.
	* Matches the prominent yellow surface in the image.
	* Scale...........wide, deep and thin (like a real cutting board)
	* Position........centered on the table, slightly above the plane
	*************************************************************************/
	
	SetTransformations(
		glm::vec3(7.0f, 0.15f, 3.5f),// wide, deep, thin board
		0.0f, 0.0f, 0.0f, // no rotation required
		glm::vec3(0.0f, 0.08f, 0.5f));// centered, just above the plane
	SetShaderTexture("yellow_wood"); // select yellow wood texture for the cutting board
	SetTextureUVScale(1.0f, 1.0f); // 1x1 scale maps the image around the cutting board without tiling
	SetShaderMaterial("boardMaterial"); // apply board material
	m_basicMeshes->DrawBoxMesh(); // Draws Box for the cutting board

	/************************************************************************
	* --- OBJECT 3: MUG BODY (Cylinder) ---
	* Represents the main body of the coffee mug.
	* A real mug is taller than it is wide, so Y is scaled up.
	* Placed at the center-right area of the board.
	* Ceramic texture wraps once around (UV 1x1) for a clean look.
	* This is one half of the complex mug object (with the torus).
	*************************************************************************/

	SetTransformations(
		glm::vec3(0.85f, 2.0f, 0.85f), //Radius-like x/z, height y
		0.0f, 0.0f, 0.0f, //No Rotation required for this shape
		glm::vec3(-0.3f, 0.16f, 0.2f)); //on top of the cutting board
	SetShaderTexture("ceramic"); //Select the ceramic texture for the mug body
	SetTextureUVScale(1.0f, 1.0f); // 1x1 scale maps the image once around the cylinder without tiling
	SetShaderMaterial("ceramicMaterial"); // apply ceramic material
	m_basicMeshes->DrawCylinderMesh(); //Draws Mesh for the Cylinder

	/**************************************************************************
	* --- OBJECT 4: MUG HANDLE (Torus) ---
	* Represents the handle of the coffee mug.
	* A torus is a donut shape, which is perfect for a mug handle.
	* Positioned flush against the cylinder wall (x = 0.6 from mug)
	* and centered on the mug's height (y = 1.16 = 0.16 base + 1.0).
	* Uses a fabric/woven texture, different from the ceramic body.
	* 
	* A 2x2 scale repeats the weave twice around the ring so the
	* fabric detail appears at the right density for the handle's size.
	***************************************************************************/

	SetTransformations(
		glm::vec3(0.5f, 0.5f, 0.5f), // small and thin like a real handle
		0.0f, 0.0f, 0.0f, //No rotation required for the torus
		glm::vec3(0.6f, 1.16f, 0.3f)); //Flush to cylinder wall, centered on mug height
	SetShaderTexture("fabric"); //Select the fabric texture for the mug handle
	
	// 2x2 tiling keeps the weave pattern fine enough to look realistic
	// on a small handle rather than a single oversized tile.
	SetTextureUVScale(2.0f, 2.0f); 
	SetShaderMaterial("fabricMaterial"); //apply fabric material
	m_basicMeshes->DrawTorusMesh(); //Draw Mesh for the torus

	/***************************************************************************
	* --- OBJECT 5: RAMEKIN BOWL (Tapered Cylinder) ---
	* A small brown clay/terra cotta ramekin bowl.
	* Matches the small brown bowl to the right of the mug in the image.
	* A tapered cylinder is wider at the top than the bottom,
	* which naturally approximates a ramekin or small bowl shape.
	* Flipped 180 degrees (X) so it looks like a real ramekin bowl.
	****************************************************************************/
	
	SetTransformations(
		glm::vec3(0.7f, 0.6f, 0.7f),   //small radius, short height
		180.0f, 0.0f, 0.0f, //180 degree X rotation
		glm::vec3(1.8f, 0.76f, 0.2f)); //to the right of the mug, on board
	SetShaderTexture("clay"); //Select clay texture for bowl
	SetTextureUVScale(1.0f, 1.0f); //1x1 scale wraps texture once around the ramekin bowl
	SetShaderMaterial("clayMaterial"); //apply clay material
	m_basicMeshes->DrawTaperedCylinderMesh(); //Draw Tapered Cylinder for the bowl

	/******************************************************************************
	* --- OBJECT 6: FORK (Box) ---
	* A flat elongated box approximating a dinner fork.
	* Laid flat on the cutting board, rotated slightly to match the
	* diagonal angle visible in the reference photo.
	* Scale: very long (Z), narrow (X), and very thin (Y).
	* Metal texture with high specular gives a stainless steel look.
	*******************************************************************************/

	SetTransformations(
		glm::vec3(0.22f, 0.07f, 2.4f),  //long, narrow, flat for visibility
		0.0f, 10.0f, 0.0f,  //slight Y rotation
		glm::vec3(-2.0f, 0.2f, 0.3f)); //left side of the cutting board
	SetShaderTexture("metal");  //select metal texture for the fork
	SetTextureUVScale(1.0f, 6.0f); //tile along length for steel grain effect
	SetShaderMaterial("metalMaterial"); //apply metal material
	m_basicMeshes->DrawBoxMesh();   //Draw Box for the fork

	/******************************************************************************
	* --- OBJECT 7: KNIFE (Box) ---
	* A thin elongated box approximating a dinner knife.
	* Placed parallel to the form, slightly to its right.
	* Scale: very long (Z), narrow (X), extremely thin (Y).
	* Same metal texture as the fork for visual consistency.
	*******************************************************************************/

	SetTransformations(
		glm::vec3(0.14f, 0.07f, 2.4f),  //long, narrow, very thin blade
		0.0f, 10.0f, 0.0f,  //slight Y rotation
		glm::vec3(-1.5f, 0.2f, 0.3f)); //just right of the fork
	SetShaderTexture("metal"); //select metal texture for the knife
	SetTextureUVScale(1.0f, 6.0f);  //tile along length for steel grain effect
	SetShaderMaterial("metalMaterial"); //apply metal material
	m_basicMeshes->DrawBoxMesh();  //Draw Box for the Knife
}
