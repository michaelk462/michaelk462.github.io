# *****CODE INFORMATION*****
# Name: Michael King
# Date: 7/17/2026
# File: view_manager.py
# Assignment: CS-499 Enhancement 1
# CS-330 3D Scene Python Port
# University: SNHU

# Python Port of ViewManager.h/ViewManager.cpp from CS-330 (C++/OpenGL).
# ORIGINALLY MADE BY: Brian Battersby (SNHU Instructor).
# MODIFIED BY: Michael King
# Adapted for CS-499 Software Engineering Enhancement by Michael King
# PORTED TO PYTHON/PyOpenGL BY: Michael King

# The ViewManager class handles:
# - Building the Camera instance with the scene's initial position/orientation
# - Processing keyboard input each frame (WASD + Q/E + P/O + ESC)
# - Processing mouse-look input (cursor delta -> yaw/pitch)
# - Processing scroll-wheel input (movement speed adjustment)
# - Building the view and projection matrices each frame
# - Uploading view, projection and viewPosition uniforms to the shader

# Key Differences from C++:
# - GLFW callbacks are replaced with Pygame event polling. Pygame is the
#   windowing system used by this Python port in place of GLFW/GLEW)
# - Static callback pattern is replaced with instance methods
# - glm::mat4 is replaced with pyrr matrix functions and numpy arrays

# CONTROLS (IDENTICAL TO THE C++ VERSION):  
# W / S...................Move Forward/Backward
# A / D...................Pan Left/Right
# Q / E...................Move Up/Down
# Mouse...................Look Around (Yaw/Pitch)
# Scroll Wheel............Adjust Camera Speed
# P.......................Perspective (3D) projection
# O.......................Orthographic (2D) projection
# ESC.....................Quit

# *** Python Imports ***
import numpy as np
import pyrr
import pygame

from shader_manager import ShaderManager
from camera import (Camera, FORWARD, BACKWARD, LEFT, RIGHT, UP, DOWN)

# *****************************************************************************
# WINDOW DIMENSIONS; match ViewManager.cpp namespace constants
# *****************************************************************************
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# *****************************************************************************
# SHADER UNIFORM NAMES; match the GLSL uniform declarations
# *****************************************************************************
U_VIEW       = "view"
U_PROJECTION = "projection"
U_VIEW_POS   = "viewPosition"

# *****************************************************************************
# Default camera movement speed and scroll step
# From ViewManager.cpp
# *****************************************************************************
DEFAULT_SPEED = 2.5  #units per second
SPEED_STEP    = 0.5  #units per second per scroll tick
SPEED_MIN     = 0.5  #minimum scroll speed
SPEED_MAX     = 20.0 #maximum scroll speed

class ViewManager:
    '''
    Manages the 3D view: camera, input processing, and matrix uploads.

    Mirrors ViewManager.h / ViewManager.cpp from CS-330.
    Replaces GLFW callbacks with Pygame event handling.
    '''

    def __init__(self, shader_manager: ShaderManager):
        '''
        Initialize the view manager and the camera.

        Mirrors ViewManager::ViewManager() from ViewManager.cpp
        Sets the camera's initial position, orientation, FOV, and
        speed to the same values use in the C++ version.

        ARGS:
        shader_manager: The active ShaderManager.
                        Receives view and projection matrix uploads
                        each frame.
        '''
        self._shader = shader_manager

        # Instantiate the camera
        # Mirrors "g_pCamera = new Camera()" in C++
        self._camera = Camera()
    

        #--- Initial camera values from ViewManager.cpp ---
        #Place the camera above and behind the scene center so that all
        #objects are visible when the application launches
        self._camera.position = np.array([0.0, 5.0, 12.0], dtype=np.float32)

        #Aim slightly downward so that the scene appears centered on screen
        #Front is normalized internally by the Camera class
        self._camera.front = np.array([0.0, -0.5, -2.0], dtype=np.float32)
        self._camera.front /= np.linalg.norm(self._camera.front)

        #World-up vector keeps the camera from rolling sideways
        self._camera.world_up = np.array([0.0, 1.0, 0.0], dtype=np.float32)

        #80-degree FOV matches g_pCamera->Zoom = 80 in C++ constructor
        self._camera.zoom = 80.0

        #Movement speed; matches the default gMovementSpeed
        self._camera.movement_speed = DEFAULT_SPEED

        # *** Mouse Tracking State ***
        # Mirrors gLastX, gLastY, gFirstMouse
        self._last_x      = WINDOW_WIDTH  / 2.0
        self._last_y      = WINDOW_HEIGHT / 2.0
        self._first_mouse = True # Prevents a jump on the first move

        # *** Frame Timing ***
        # Mirrors gDeltaTime / gLastFrame
        self._last_frame_ms = pygame.time.get_ticks()

        # *** Projection Mode Toggle ***
        # Mirrors bOrthographicProjection
        self._orthographic = False # False = perspective (3D); True = orthographic (2D)
        
        # *** Key State Tracker for Toggle Debouncing ***
        # P / O keys
        self._prev_keys = pygame.key.get_pressed()

    # *****************************************************************************
    # Public API
    # *****************************************************************************

    @property
    def camera(self) -> Camera:
        '''expose the camera for external read (e.g., main loop HUD)'''
        return self._camera

    @property
    def should_quit(self) -> bool:
        '''true if the user pressed ESC or closed the window'''
        return self._quit_flag
    
    def prepare_scene_view(self) -> bool:
        '''
        Compute delta time, process input, build matrices, upload to shader.

        Mirrors ViewManager::PrepareSceneView() from ViewManager.cpp
        Must be called once per frame before drawing.

        Returns true if the application should continue; 
        false if ESC was pressed.
        '''
        # *** DELTA TIME; mirrors gDeltaTime computation ***
        now_ms     = pygame.time.get_ticks()
        delta_time = (now_ms - self._last_frame_ms) / 1000.0 # seconds
        self._last_frame_ms = now_ms

        # *** Poll Keyboard and Mouse ***
        if not self._process_keyboard(delta_time):
            return False  # ESC Pressed; signal the main loop to exit
        self._process_mouse_events()

        # *** Build View Matrix from Current Camera State ***
        view = self._camera.get_view_matrix()

        # *** Build projection matrix (Perspective or Orthographic) ***
        if self._orthographic:
            #Orthographic: scale=0.01 converts world units to NDC
            #Matches glm::ortho() call in ViewManager.cpp
            scale = 0.01
            projection = pyrr.matrix44.create_orthogonal_projection(
                left   = -WINDOW_WIDTH  * scale,
                right  =  WINDOW_WIDTH  * scale,
                bottom = -WINDOW_HEIGHT * scale,
                top    =  WINDOW_HEIGHT * scale,
                near   = 0.1,
                far    = 100.0,
                dtype  = np.float32,
            )
        else:
            #Perspective: standard 3D projection
            projection = pyrr.matrix44.create_perspective_projection(
                fovy = self._camera.zoom,
                aspect = WINDOW_WIDTH / WINDOW_HEIGHT,
                near = 0.1,
                far = 100.0,
                dtype = np.float32,
            )
        
        # *** Upload Matrices to the Shader ***
        self._shader.set_mat4("view",       view)
        self._shader.set_mat4("projection", projection)
        self._shader.set_vec3("viewPosition",
                              *self._camera.position.tolist())
        
        return True
    
    def handle_event(self, event: pygame.event.Event):
        '''
        Handle a single Pygame event.

        Called by the main loop for events that must be processed outside of the 
        per-frame keyboard poll, specifically scroll-wheel events.

        Mirrors Mouse_Scroll_Callback() in ViewManager.cpp

        ARGS:
        event: A Pygame event object.
        '''
        if event.type == pygame.MOUSEWHEEL:       
            #SCROLL UP (y > O): increase speed
            #SCROLL DOWN (y < 0): decrease speed
            #Multiply by SPEED_STEP (0.5) per tick; matches C++ yOffset * 0.5
            new_speed = self._camera.movement_speed + event.y * SPEED_STEP
            new_speed = max(SPEED_MIN, min(SPEED_MAX, new_speed))
            if new_speed != self._camera.movement_speed:
                self._camera.movement_speed = new_speed
                print(f"Camera movement speed: {new_speed:.1f}")

    # *****************************************************************************
    # PRIVATE INPUT HELPERS
    # *****************************************************************************
    def _process_keyboard(self, delta_time: float) -> bool:
        '''
        Poll the keyboard state and apply camera movements.

        Mirrors ViewManager::ProcessKeyboardEvents() from ViewManager.cpp.
        Multiple keys can be held simultaneously (e.g. W+D = move diagonally).

        ARGS:
        delta_time: Elapsed seconds since last frame for speed scaling.

        Returns False if ESC was pressed (signals the main loop to quit), 
                True otherwise.
        '''
        keys = pygame.key.get_pressed()

        #ESC: Close the Application
        if keys[pygame.K_ESCAPE]:
            return False
        
        # W / S: Forward / Backward
        if keys[pygame.K_w]:
            self._camera.process_keyboard(FORWARD, delta_time)
        if keys[pygame.K_s]:
            self._camera.process_keyboard(BACKWARD, delta_time)

        # A / D: Strafe Left / Right
        if keys[pygame.K_a]:
            self._camera.process_keyboard(LEFT, delta_time)
        if keys[pygame.K_d]:
            self._camera.process_keyboard(RIGHT, delta_time)

        # Q / E: Move Up / Down
        if keys[pygame.K_q]:
            self._camera.process_keyboard(UP, delta_time)
        if keys[pygame.K_e]:
            self._camera.process_keyboard(DOWN, delta_time)

        # P: Switch to Perspective (3D) projection; debounced
        if keys[pygame.K_p] and not self._prev_keys[pygame.K_p]:
            self._orthographic = False
            print("Projection: PERSPECTIVE")

        # O: Switch to Orthographic (2D) projection; debounced
        if keys[pygame.K_o] and not self._prev_keys[pygame.K_o]:
            self._orthographic = True
            print("Projection: ORTHOGRAPHIC")
        
        self._prev_keys = keys
        return True
    
    def _process_mouse_events(self):
        '''
        Compute cursor delta from the current relative mouse motion
        and forward it to the camera for look-around.

        Mirrors Mouse_Position_Callback() in ViewManager.cpp.
        In Pygame, pygame.mouse.get.rel() returns the pixel delta since the
        last call; equivalent to the (xMousePos - gLastX) calculation in C++.
        The mouse is captured with MOUSEMOTION in relative mode.
        '''
        dx, dy = pygame.mouse.get_rel()
        if dx == 0 and dy == 0:
            return
        
        # Invert Y so that moving the mouse up pitches the camera upward,
        # matching the "yOffset = gLastY - yMousePos" inversion in C++.
        self._camera.process_mouse_movement(float(dx), float(-dy))