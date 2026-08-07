///////////////////////////////////////////////////////////////////////////////
// viewmanager.h
// ============
// manage the viewing of 3D objects within the viewport
//
//  AUTHOR: Brian Battersby - SNHU Instructor / Computer Science
//	Created for CS-330-Computational Graphics and Visualization, Nov. 1st, 2023
// 
// MODIFIED BY: Michael King
// *************************************
// *         MILESTONE THREE           *
// *************************************
// 
// CHANGES MADE: Added static Mouse_Scroll_Callback() declaration 
//               to ViewManager.h
//  PURPOSE: Allows GLFW to invoke the scroll handler defined in
//           ViewManager.cpp whenever the user turns the scroll wheel.
//           The callback adjusts the camera movement speed at runtime.
///////////////////////////////////////////////////////////////////////////////

#pragma once

#include "ShaderManager.h"
#include "camera.h"

// GLFW library
#include "GLFW/glfw3.h" 

/*************************************************************
* --- GLFW Static Callbacks ---
* These *must* be static so their address can be passed
* directly to the GLFW callback registration functions
* (which expect a plain C function pointer,
* not a member function pointer).
**************************************************************/

class ViewManager
{
public:
	// constructor
	ViewManager(
		ShaderManager* pShaderManager);
	// destructor
	~ViewManager();

	// Called by GLFW on every cursor-move event
	// Computes the horizontal (yaw) and vertical (pitch) deltas and
	// forwards them to the camera so it can update its orientation
	static void Mouse_Position_Callback(GLFWwindow* window, double xMousePos, double yMousePos);

private:
	// pointer to shader manager object
	ShaderManager* m_pShaderManager;
	// active OpenGL display window
	GLFWwindow* m_pWindow;

	// Called by GLFW on every scroll-wheel event.
	// Increases the camera movement speed when scrolling up and
	// Decreases it when scrolling down. Speed is clamped to [0.5, 20.0].
	static void Mouse_Scroll_Callback(GLFWwindow* window, double xOffset, double yOffset);

	// process keyboard events for interaction with the 3D scene
	void ProcessKeyboardEvents();

public:
	// create the initial OpenGL display window
	// sets up the OpenGl content
	// register all input callbacks
	// return window handle to the caller
	GLFWwindow* CreateDisplayWindow(const char* windowTitle);
	
	// prepare the conversion from 3D object display to 2D scene display
	// Called once per frame from the render loop
	// computes gDeltaTime and polls input,
	// builds the view and projection matrices from current camera state,
	// and uploads them to the shader program
	void PrepareSceneView();
};