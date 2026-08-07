///////////////////////////////////////////////////////////////////////////////
// viewmanager.h
// ============
// manage the viewing of 3D objects within the viewport
//
//  AUTHOR: Brian Battersby - SNHU Instructor / Computer Science
//	Created for CS-330-Computational Graphics and Visualization, Nov. 1st, 2023
// 
//  MODIFIED BY: Michael King
//  ********************************************
//  *            MILESTONE THREE               *
//  ********************************************
//  CHANGES MADE:
//  - Implemented Mouse_Position_Callback() for look-around (pitch/yaw)
//  - Implemented scroll callback for camera speed adjustment
//  - Implemented WASD + QE keyboard camera navigation
//  - Enabled cursor capture for smooth mouse look
// 
//  *********************************************
//  *             FINAL PROJECT                 *
//  *********************************************
//  CHANGES MADE:
//  - Added P / O key toggle between perspective and orthographic projection
//    P key = Perspective (3D)
//    O key = Orthographic (2D)
//  - bOrthographicProjection flag switches which glm matrix is built
//    in PrepareSceneView() and uploaded to the shader each frame.
//  - Camera stays in the same orientation when switching projections.
// 
// CONTROLS:
// - W / S.................Forward (zoom in) / Backward (zoom out)
// - A / D.................Pan Left/Right
// - Q / E.................Move Up/Down
// - Mouse.................Look Around (Yaw / Pitch)
// - Scroll Up.............Increase Camera Movement Speed
// - Scroll Down...........Decrease Camera Movement Speed
// - P.....................Switch to Perspective (3D) view
// - O.....................Switch to Orthographic (2D) view
// - Esc...................Close Application
///////////////////////////////////////////////////////////////////////////////

#include "ViewManager.h"

// GLM Math Header inclusions
#include <glm/glm.hpp>
#include <glm/gtx/transform.hpp>
#include <glm/gtc/type_ptr.hpp>    

// declaration of the global variables and defines
namespace
{
	// Variables for window width and height
	const int WINDOW_WIDTH = 1000;
	const int WINDOW_HEIGHT = 800;

	//Uniform names must match the variable names declared in vertex shader
	const char* g_ViewName = "view";
	const char* g_ProjectionName = "projection";

	// camera object used for viewing and interacting with
	// the 3D scene
	Camera* g_pCamera = nullptr;

	// these variables are used for mouse movement processing
	float gLastX = WINDOW_WIDTH / 2.0f;
	float gLastY = WINDOW_HEIGHT / 2.0f;
	bool gFirstMouse = true;

	// gDeltaTime is the elapsed time (in Seconds) between the current and previous frame.
	// Multiplying movement amounts by gDeltaTime keeps camera speed consistent regardless
	// of how fast or slow the machine is rendering frames.
	float gDeltaTime = 0.0f;
	float gLastFrame = 0.0f;

	//Camera movement speed is adjusted by mouse scroll wheel
	//The default is 2.5 units/sec
	//Scroll up increases
	//Scroll down decreases
	//Clamped to [0.5, 20.0] so it remains usable
	float gMovementSpeed = 2.5f;

	//This variable is false when orthographic projection is off
	//and true when it is on
	bool bOrthographicProjection = false;
}

/***********************************************************
 *  ViewManager()
 *
 *  The constructor for the class
 ***********************************************************/
ViewManager::ViewManager(
	ShaderManager *pShaderManager)
{
	//Store the ShaderManager pointer so PrepareSceneView() can
	//upload the view and projection matrices to the GPU each frame.
	m_pShaderManager = pShaderManager;
	m_pWindow = NULL;
	g_pCamera = new Camera(); //allocate the camera object on the heap.
	
	// default camera view parameters
	// Place the camera above and behind the origin
	// so all scene objects are visible when app launches
	g_pCamera->Position = glm::vec3(0.0f, 5.0f, 12.0f);

	//Aim slightly downward towards the scene center so it
	//appears centered on the screen.
	g_pCamera->Front = glm::vec3(0.0f, -0.5f, -2.0f);

	//World up vector
	//keeps the camera from rolling sideways
	g_pCamera->Up = glm::vec3(0.0f, 1.0f, 0.0f);

	//Field-of-view angle in degrees
	//Used when building the projection matrix
	g_pCamera->Zoom = 80;

	//Apply Initial Movement Speed to the camera
	g_pCamera->MovementSpeed = gMovementSpeed;
}

/***********************************************************
 *  ~ViewManager()
 *
 *  The destructor for the class
 ***********************************************************/
ViewManager::~ViewManager()
{
	// Null out the borrowed pointer
	// This class does not own the Shader Manager.
	m_pShaderManager = NULL;
	m_pWindow = NULL;

	//Free the camera that was allocated in the constructor.
	if (NULL != g_pCamera)
	{
		delete g_pCamera;
		g_pCamera = NULL;
	}
}

/***********************************************************
 *  CreateDisplayWindow()
 *
 *  Creates the GLFW window and OpenGL context.
 *  Registers all three input callbacks:
 *  - Cursor
 *  - Scroll
 *  - Keyboard (glfwGetKey)
 *  Returns the window handle to the caller (main.cpp)
 ***********************************************************/
GLFWwindow* ViewManager::CreateDisplayWindow(const char* windowTitle)
{
	GLFWwindow* window = nullptr;

	// try to create the displayed OpenGL window
	// pass NULL for monitor to keep it windowed, not Fullscreen.
	window = glfwCreateWindow(
		WINDOW_WIDTH,
		WINDOW_HEIGHT,
		windowTitle,
		NULL, NULL);
	if (window == NULL)
	{
		//Window creation fails if the requested OpenGL version is unsupported.
		std::cout << "Failed to create GLFW window" << std::endl;
		glfwTerminate();
		return NULL;
	}

	//Make this window's OpenGL context active on the calling thread
	glfwMakeContextCurrent(window);

	// Register the cursor-movement callback
	// GLFW invokes this function automatically whenever the mouse
	// moves inside the window.
	// It feeds the new cursor coordinates to Mouse_Position_Callback(),
	// which computes the delta and calls g_pCamera->ProcessMouseMovement().
	glfwSetCursorPosCallback(window, &ViewManager::Mouse_Position_Callback);

	// Register the scroll-wheel callback.
	// GLFW invokes this function automatically on every scroll event.
	// It adjusts gMovement speed and pushes the new value into the camera object.
	glfwSetScrollCallback(window, &ViewManager::Mouse_Scroll_Callback);

	// Hide and confine the cursor to the window for FPS-style look around.
	// Without GLFW_CURSOR_DISABLED, the cursor stays visible and can leave the window,
	// which can break the mouse-delta calculation in the callback.
	glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_DISABLED);

	// enable blending for supporting transparent rendering
	glEnable(GL_BLEND);
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

	m_pWindow = window;

	return(window);
}

/***********************************************************
 *  Mouse_Position_Callback()
 *
 *  This method is automatically called from GLFW whenever
 *  the mouse is moved within the active GLFW display window.
 * 
 *  It calculates how far the cursor moved
 *  (xOffset, yOffset)
 * 
 *	Passes those offsets to the camera so it can update the
 *  yaw (left / right) and
 *  pitch (up / down) angles.
 ***********************************************************/
void ViewManager::Mouse_Position_Callback(GLFWwindow* window, double xMousePos, double yMousePos)
{
	// when the first mouse move event is received, this needs to be recorded so that
	// all subsequent mouse moves can correctly calculate the
	// X position offset and Y position offset for proper operation

	if (gFirstMouse) {
		gLastX = xMousePos;
		gLastY = yMousePos;
		gFirstMouse = false;
	}

	//calculate the X offset and the Y offset values for moving the 3D camera accordingly
	float xOffset = xMousePos - gLastX;
	float yOffset = gLastY - yMousePos; //reversed since the y-coordinates go from bottom to top

	//set the current positions into the last position variables
	gLastX = xMousePos;
	gLastY = yMousePos;

	// Move the 3D Camera according to the calculated offsets
	g_pCamera->ProcessMouseMovement(xOffset, yOffset);
}

/***********************************************************
 * Mouse_Scroll_Callback()
 *
 * Called by GLFW on every scroll-wheel event.
 * Increases or decreases the camera movement speed so the
 * user can navigate large or tight scenes.
 *
 * --- Method Controls --
 * SCROLL UP.........Increase Camera Movement Speed
 *                   +0.5/tick
 * SCROLL DOWN.......Decrease Camera Movement Speed
 *                   -0.5/tick
 * SPEED.............[0.5, 20.0] to stay usable and stable.
 * 
 * --- Parameters ---
 * window............GLFW window that received the event.
 * xOffset...........Horizontal scroll amount (not used here)
 * yOffset...........Vertical scroll
 *                   +1.0/tick up; -1.0/tick down
 ************************************************************/

void ViewManager::Mouse_Scroll_Callback(GLFWwindow* window, double xOffset, double yOffset) {
	
	// Scroll up = yOffset is positive
	// Scroll down = yOffset is negative
	// Multiply by 0.5 so each scroll tick makes a small change
	gMovementSpeed += static_cast<float>(yOffset) * 0.5f;

	//Lower bound: prevent the speed from reaching 0 or below,
	//which would freeze or reverse all keyboard movement
	if (gMovementSpeed < 0.5f) gMovementSpeed = 0.5f;

	//Upper bound: prevent the speed from becoming so large that a
	//single frame moves the camera entirely across the scene.
	if (gMovementSpeed > 20.0f) gMovementSpeed = 20.0f;

	//Push the updated speed into the camera so ProcessKeyboard()
	//picks it up on the very next frame
	if (g_pCamera != NULL) {
		g_pCamera->MovementSpeed = gMovementSpeed;
	}

	//Display current speed on the console for verification/debugging
	std::cout << "Camera movement speed: " << gMovementSpeed << std::endl;
}


/***********************************************************
 *  ProcessKeyboardEvents()
 *
 *  Polls the keyboard state once per frame and issues the
 *  appropriate movement command to the camera.
 *  Multiple keys may be held simultaneously for combined
 *  movement.
 * 
 * Example:
 * W + D..........Move forward and right at the same time.
 * 
 * All movement is scaled by gDeltaTime
 * (computed in PrepareSceneView)
 * so speed stays consistent across different frame rates.
 * 
 * CONTROLS:
 * W / S..........Move Forward  (Zoom In)
 *                Move Backward (Zoom Out)
 * A / D..........Pan Left
 *                Pan Right (Strafe)
 * Q / E..........Move Up
 *                Move Down
 * ESC............Close Application
 ***********************************************************/
void ViewManager::ProcessKeyboardEvents()
{
	// signal GLFW to close the window if ESC key is pressed
	if (glfwGetKey(m_pWindow, GLFW_KEY_ESCAPE) == GLFW_PRESS)
	{
		glfwSetWindowShouldClose(m_pWindow, true);
	}

	//Nothing below can execute safely without a valid camera pointer
	if (NULL == g_pCamera) { return; }

	// ---- W / S: Forward and Backward (Zooming In and Out) ----
	// The camera moves along its front vector so it always advances or
	// retreats in exactly the direction the user is looking
	if (glfwGetKey(m_pWindow, GLFW_KEY_W) == GLFW_PRESS)
	{
		g_pCamera->ProcessKeyboard(FORWARD, gDeltaTime); //PRESS W
	}if (glfwGetKey(m_pWindow, GLFW_KEY_S) == GLFW_PRESS)
	{
		g_pCamera->ProcessKeyboard(BACKWARD, gDeltaTime); //PRESS S
	}

	// ---- A / D: Pan Left and Right (Strafe) ----
	// The camera moves along its right vector, which is perpendicular to the front.
	// This slides the camera horizontally without changing its aim.
	if (glfwGetKey(m_pWindow, GLFW_KEY_A) == GLFW_PRESS) {
		g_pCamera->ProcessKeyboard(LEFT, gDeltaTime); //PRESS A
	} if (glfwGetKey(m_pWindow, GLFW_KEY_D) == GLFW_PRESS) {
		g_pCamera->ProcessKeyboard(RIGHT, gDeltaTime); //PRESS D
	}

	// ---- Q / E: Move Up and Down (Vertical) ----
	// The camera moves along the up vector, rising/sinking vertically,
	// regardless of which horizontal direction it is facing.
	if (glfwGetKey(m_pWindow, GLFW_KEY_Q) == GLFW_PRESS) {
		g_pCamera->ProcessKeyboard(UP, gDeltaTime); //PRESS Q
	} if (glfwGetKey(m_pWindow, GLFW_KEY_E) == GLFW_PRESS) {
		g_pCamera->ProcessKeyboard(DOWN, gDeltaTime); //PRESS E
	}

	// ---- P: Switch to Perspective (3D) Projection ----
	// Pressing P restores the standard 3D perspective view.
	// The camera stays in its current position and orientation.
	if (glfwGetKey(m_pWindow, GLFW_KEY_P) == GLFW_PRESS) {
		bOrthographicProjection = false;
	}

	// ---- O: Switch to Orthographic (2D) Projection ----
	// Pressing O flattens the view to a 2D orthographic projection.
	// The camera stays in its current position and orientation.
	if (glfwGetKey(m_pWindow, GLFW_KEY_O) == GLFW_PRESS) {
		bOrthographicProjection = true;
	}
}

/***********************************************************
 *  PrepareSceneView()
 *
 *  This method is used for preparing the 3D scene by loading
 *  the shapes, textures in memory to support the 3D scene 
 *  rendering
 * 
 * Responsibilities:
 * 1. Compute gDeltaTime for frame-rate-independent movement.
 * 2. Poll keyboard input via ProcessKeyboardEvents().
 * 3. Retrieve the current view matrix from the camera.
 * 4. Build the projection matrix: either perspective (3D)
 *    or orthographic (2D) depending on bOrthographicProjection.
 * 5. Upload view, projection, and camera position to the shader.
 * 
 * The P / O keys in ProcessKeyboardEvents() toggle
 * bOrthographicProjection, causing this function to switch
 * which matrix is sent to the GPU on the next frame.
 ***********************************************************/
void ViewManager::PrepareSceneView()
{
	glm::mat4 view;
	glm::mat4 projection;

	// per-frame timing
	float currentFrame = glfwGetTime();
	gDeltaTime = currentFrame - gLastFrame;
	gLastFrame = currentFrame;

	// process any keyboard events that may be waiting in the 
	// event queue
	ProcessKeyboardEvents();

	// get the current view matrix from the camera
	view = g_pCamera->GetViewMatrix();

	//Build the projection matrix based on the current mode.
	if (bOrthographicProjection) {

		// ORTHOGRAPHIC (2D) PROJECTION
		// Projects the scene without perspective foreshortening.
		// Objects appear the same size regardless of their distance.
		// The visible volume is defined by left/right/bottom/top/near/far.
		// Scale factor of 0.01 coverts from pixel-like coordinates to
		// world units
		float scale = 0.01f;
		projection = glm::ortho(
			-(float)WINDOW_WIDTH * scale,  //left
			(float)WINDOW_WIDTH * scale,   //right
			-(float)WINDOW_HEIGHT * scale, //bottom
			(float)WINDOW_HEIGHT * scale,  //top
			0.1f,                          //near clip
			100.0f);                       //far clip
	}
	else {
		// PERSPECTIVE (3D) PROJECTION
		// Projects the scene with perspective foreshadowing so distant
		// objects appear smaller; the standard 3D view.
		projection = glm::perspective(
			glm::radians(g_pCamera->Zoom),                  //Field of view
			(GLfloat)WINDOW_WIDTH / (GLfloat)WINDOW_HEIGHT, //Aspect Ratio
			0.1f,                                           //near clip pane
			100.0f);                                        //far clip pane
	}

	// if the shader manager object is valid
	if (NULL != m_pShaderManager)
	{
		// set the view matrix into the shader for proper rendering
		m_pShaderManager->setMat4Value(g_ViewName, view);
		// set the view matrix into the shader for proper rendering
		m_pShaderManager->setMat4Value(g_ProjectionName, projection);
		// set the view position of the camera into the shader for proper rendering
		m_pShaderManager->setVec3Value("viewPosition", g_pCamera->Position);
	}
}