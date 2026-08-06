# *****CODE INFORMATION*****
# Name: Michael King
# Date: 7/17/2026
# File: main.py
# Assignment: CS-499 Enhancement 1
# CS-330 3D Scene Python Port
# University: SNHU

# Python Port of MainCode.cpp from CS-330 (C++/OpenGL).
# ORIGINALLY MADE BY: Brian Battersby (SNHU Instructor).
# MODIFIED BY: Michael King
# Adapted for CS-499 Software Engineering Enhancement by Michael King
# PORTED TO PYTHON/PyOpenGL BY: Michael King

# This file is the application entry point. It mirrors the structure of
# MainCode.cpp: Initialize the window, load shaders, prepare the scene, then
# run the render loop until the user closes the application.

# ARCHITECTURE COMPARISON:
# -----------------------------------------------------------------------
# C++ role      | Python Equivalent
# --------------|--------------------------------------------------------
# GLFW          | Pygame (Windowing and Input)
# GLEW          | PyOpenGL (OpenGL extension loader)
# ShaderManager | shader_manager.ShaderManager
# ViewManager   | view_manager.ViewManager
# SceneManager  | scene_manager.SceneManager
# ShapeMeshes   | shape_meshes.ShapeMeshes (used by SceneManager)
# Camera        | camera.Camera            (used by ViewManager)
# stb.image.h   | Pillow/PIL.Image         (used by SceneManager)
# glm           | pyrr and numpy           (used throughout)

# CONTROLS:  
# W / S...................Move Forward/Backward
# A / D...................Pan Left/Right
# Q / E...................Move Up/Down
# Mouse...................Look Around (Yaw/Pitch)
# Scroll Up...............Increase Camera Movement Speed
# Scroll Down.............Decrease Camera Movement Speed
# P.......................Perspective (3D) projection
# O.......................Orthographic (2D) projection
# ESC.....................Quit

# Run this port by typing the following in the terminal:
# `python main.py`

# Required Dependencies (install with pip):
# pygame PyOpenGL PyOpenGL_accelerate Pillow numpy pyrr

# For Python 3.14+:
# pygame-ce PyOpenGL PyOpenGL_accelerate Pillow numpy pyrr

# ***Python Imports***
import sys
import os

import pygame
from pygame.locals import DOUBLEBUF, OPENGL

from OpenGL.GL import (
    glEnable, glClearColor, glClear, glBlendFunc,
    GL_DEPTH_TEST, GL_BLEND,
    GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA,
    GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT,
    glGetString, GL_VERSION,
)

from shader_manager import ShaderManager
from view_manager import ViewManager, WINDOW_WIDTH, WINDOW_HEIGHT
from scene_manager import SceneManager

# *********************************************************
# Window Title: Mirrors WINDOW_TITLE in MainCode.cpp
# *********************************************************
WINDOW_TITLE = "CS-330 Python Port - 7-1 Final Project"

# ****************************************************************
# Shader and texture paths relative to this script's directory
# ****************************************************************
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SHADER_DIR = os.path.join(SCRIPT_DIR, "shaders")
VERTEX_SHADER = os.path.join(SHADER_DIR, "vertex_shader.glsl")
FRAG_SHADER = os.path.join(SHADER_DIR, "fragment_shader.glsl")

def initialize_pygame() -> bool:
    '''
    Initialize Pygame and create the OpenGL backend display window.

    Mirrors InitializeGLFW() and the CreateDisplayWindow() call in
    MainCode.cpp/ViewManager.cpp.

    Pygame replaces GLFW as the windowing and event system.

    Returns: True on success and false if Pygame initialization fails.
    '''

    pygame.init()

    # Request an OpenGL 3.3 core-profile context; equivalent to the
    # glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR/MINOR, ...) calls in C++
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK,
                                    pygame.GL_CONTEXT_PROFILE_CORE)
    pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)

    try:
        pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
            DOUBLEBUF | OPENGL,
        )
        pygame.display.set_caption(WINDOW_TITLE)
    except pygame.error as e:
        print(f"Failed to create Pygame window: {e}")
        return False
    
    # Capture the mouse cursor for FPS-style look around
    # Mirrors glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_DISABLED)
    pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)

    return True

def print_opengl_info():
    '''
    Print the OpenGL version string to confirm successful context creation.

    Mirrors the std::cout statements in InitializeGLEW() in MainCode.cpp.
    '''
    version = glGetString(GL_VERSION)
    print("OpenGL successfully initialized")
    print(f"OpenGL version: {version.decode()}\n")

def main():
    '''
    This is the application's entry point.

    Mirrors the main() function in MainCode.cpp:
    1. Initialize Pygame (replaces InitializeGLFW and CreateDisplayWindow)
    2. Print OpenGL Info (replaces InitializeGLEW)
    3. Load shaders (replaces g_ShaderManager->LoadShaders)
    4. Prepare the 3D Scene (replaces g_SceneManager->PrepareScene)
    5. Run the render loop (replaces the while(!glfwWindowShouldClose) loop)
    6. Clean up (Pygame and Python handle this automatically)
    '''

    # ***STEP 1***
    # Windowing and OpenGL Context
    if not initialize_pygame():
        sys.exit(1)

    print_opengl_info()

    #Enable alpha blending
    #Mirrors glEnable(GL_BLEND) in CreateDisplayWindow()
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # ***STEP 2***
    # Shader Program
    shader_manager = ShaderManager()
    program_id = shader_manager.load_shaders(VERTEX_SHADER, FRAG_SHADER)
    if not program_id:
        #if shaders fail to load (wrong path, compile error, etc.)
        #the program_id is 0.
        #Continuing with program 0 produces a black screen with no error message.
        #Exit cleanly instead.
        print("ERROR: Shader program failed to load. Check /shaders/ directory.")
        pygame.quit()
        sys.exit(1)
    shader_manager.use()

    # ***STEP 3***
    # View Manager (camera, input, and projection)
    view_manager = ViewManager(shader_manager)

    # ***STEP 4***
    # Scene manager (meshes, textures and materials)
    scene_manager = SceneManager(shader_manager, texture_dir=SCRIPT_DIR)
    scene_manager.prepare_scene()

    # ***** ENABLE DEPTH TEST EACH FRAME *****
    # Mirrors: glEnable(GL_DEPTH_TEST) inside the loop in MainCode.cpp
    glEnable(GL_DEPTH_TEST)

    # ***STEP 5***
    # Mirrors: while (!glfwWindowShouldClose(g_Window)) {...}
    clock = pygame.time.Clock()
    running = True

    while running:
        # ***** PROCESS PYGAME EVENTS *****
        # Mirrors: glfwPollEvents() and the static GLFW callbacks in C++
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                #Forward events to ViewManager (handles scroll wheel speed adjustment)
                view_manager.handle_event(event)
        
        # ***** ENABLE DEPTH TEST EACH FRAME *****
        # Mirrors: glEnable(GL_DEPTH_TEST) inside the loop in MainCode.cpp
        # glEnable(GL_DEPTH_TEST)

        # ***** CLEAR THE COLOR AND DEPTH BUFFERS *****
        # Mirrors: glClearColor (0.08, 0.08, 0.12, 1.0) + glClear
        glClearColor(0.08, 0.08, 0.12, 1.0) #subtle dark blue-grey background
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # ***** BUILD VIEW/PROJECTION MATRICES AND PROCESS INPUT *****
        # Mirrors: g_ViewManager->PrepareSceneView()
        if not view_manager.prepare_scene_view():
            running = False #Press ESC
            break

        # ***** DRAW ALL SCENE OBJECTS *****
        # Mirrors: g_SceneManager->RenderScene()
        scene_manager.render_scene()

        # ***** SWAP FRONT/BACK BUFFERS TO DISPLAY RENDERED FRAME *****
        # Mirrors: glfwSwapBuffers(g_Window)
        pygame.display.flip()

        # Cap at 60FPS; GLFW v-sync was implicit
        # Pygame needs an explicit cap
        clock.tick(60)
    
    # ***STEP 6***
    # Cleanup
    # Python's garbage collector and Pygame handle this automatically,
    # mirroring the "delete g_SceneManager / g_ViewManager / g_ShaderManager"
    # block at the end of the main() function in MainCode.cpp
    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()