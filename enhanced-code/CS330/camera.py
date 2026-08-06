# *****CODE INFORMATION*****
# Name: Michael King
# Date: 7/17/2026
# File: camera.py
# Assignment: CS-499 Enhancement 1
# CS-330 3D Scene Python Port
# University: SNHU

# Python Port of camera.h from CS-330 (C++/OpenGL).
# Original Source: LearnOpenGL.com (CC BY-NC 4.0)
# Adapted for CS-499 Software Engineering Enhancement by Michael King
# The Camera class implements a free-look FPS-style camera using Euler angles
# (yaw and pitch). It computes the view matrix each frame and processes keyboard
# and mouse input to update the camera's orientation and position.

# KEY DIFFERENCES FROM THE C++ VERSION:
# 1. glm::vec3/glm::mat4 are replaced with numpy arrays and pyrr utilities
# 2. GLboolean is replaced with a plain Python bool
# 3. Camera_Movement enum replaced with string constants for readability
# 4. Constructor uses keyword arguments with defaults matching the C++ defaults

# ***Python Imports***
import math
import numpy as np
import pyrr

# ************************************************************************
# Camera movement direction constants (replaces the Camera_Movement enum)
# ************************************************************************
FORWARD = "FORWARD"
BACKWARD = "BACKWARD"
LEFT = "LEFT"
RIGHT = "RIGHT"
UP = "UP"
DOWN = "DOWN"

# ************************************************************************
# Default camera parameters (match the C++ #define constants)
# ************************************************************************
DEFAULT_YAW         = -90.0 #Degrees; faces -Z by default
DEFAULT_PITCH       = 0.0   #Degrees; level with the horizon
DEFAULT_SPEED       = 2.5   #World units per second
DEFAULT_SENSITIVITY = 0.01  #Mouse sensitivity multiplier
DEFAULT_ZOOM        = 45.0  #Field of view in degrees

class Camera:
    '''
    Free-look camera for a 3D OpenGL scene

    Stores the position, Euler angles, and orientation vectors.
    Every frame, ViewManager calls get_view_matrix() to retrieve the current
    lookAt Matrix, and process_keyboard() / process_mouse_movement() to update
    the state based on the user input.

    ATTRIBUTES:
    position (np.ndarray): Camera position in world space (vec3).
    front    (np.ndarray): Normalized direction the camera is facing.
    up       (np.ndarray): Camera-local up vector.
    right    (np.ndarray): Camera-local right vector (perpendicular to front).
    world_up (np.ndarray): World-space up vector (fixed, usually [0, 1, 0]).
    yaw      (float): Horizontal rotation in degrees.
    pitch    (float): Vertical rotation in degrees, clamped to 89 degrees.
    movement_speed    (float): Units per second for keyboard movement.
    mouse_sensitivity (float): Degrees of rotation per pixel of mouse movement.
    zoom     (float): Field of view in degrees (used for perspective projection).
    '''

    def __init__(
        self,
        position: np.ndarray = None,
        world_up: np.ndarray = None,
        yaw:   float = DEFAULT_YAW,
        pitch: float = DEFAULT_PITCH,
    ):
        '''
        Initialize the camera with optional position, world-up and Euler angles.

        Defaults match the C++ Camera constructor defaults and the specific values set
        in ViewManager::ViewManager() for the CS-330 Scene.

        ARGS:
        position.......Camera position in world space (vec3).
        world_up:......World-space up vector (fixed, usually [0, 1, 0]).
        yaw............Horizontal angle in degrees.
        pitch..........Vertical angle in degrees.
        '''
        self.movement_speed = 0.5
        self.mouse_sensitivity = 0.1
        self.zoom = 45.0
        self.position = np.array(position if position is not None else [0.0, 0.0, 0.0], dtype=np.float32)
        self.world_up = np.array(world_up if world_up is not None else [0.0, 1.0, 0.0], dtype=np.float32)
        self.yaw   = yaw
        self.pitch = pitch

        # Orientation vectors computed from Euler angles
        self.front = np.array([0.0, 0.0, -1.0], dtype=np.float32)
        self.up    = np.array([0.0, 1.0,  0.0], dtype=np.float32)
        self.right = np.array([1.0, 0.0,  0.0], dtype=np.float32)
        
        # Camera options matching the C++ defaults
        self.movement_speed    = DEFAULT_SPEED
        self.mouse_sensitivity = DEFAULT_SENSITIVITY
        self.zoom              = DEFAULT_ZOOM

        # Compute the initial orientation vectors from the starting Euler angles
        self._update_camera_vectors()
    
    #******************************************************************
    # View the Matrix (mirrors Camera::GetViewMatrix())
    #******************************************************************

    def get_view_matrix(self) -> np.ndarray:
        '''
        Return the current view matrix as a (4, 4) float32 numpy array.
        
        Equivalent to glm::lookAt(Position, Position + Front, Up).
        Uses pyrr.matrix44.create_look_at(), which follows the same convention

        Returns:
        A column-major (4, 4) float32 view matrix.
        '''

        target = self.position + self.front
        return pyrr.matrix44.create_look_at(
            self.position,
            target,
            self.up,
            dtype=np.float32,
        )
    
    #******************************************************************
    # Keyboard input (mirrors Camera::ProcessKeyboard)
    #******************************************************************

    def process_keyboard(self, direction: str, delta_time: float):
        '''
        Move the camera based on a direction command and elapsed frame time.

        Multiplying by delta_time keeps speed frame-rate independent, matching the
        gDeltaTime-scaled calls in ViewManager::ProcessKeyboardEvents().

        Args:
        direction: one of the FORWARD/BACKWARD/LEFT/RIGHT/UP/DOWN constants.
        delta_time: Elapsed time since last frame in seconds.
        '''

        velocity = self.movement_speed * delta_time
        if direction == FORWARD:
            self.position += self.front * velocity
        elif direction == BACKWARD:
            self.position -= self.front * velocity
        elif direction == LEFT:
            self.position -= self.right * velocity
        elif direction == RIGHT:
            self.position += self.right * velocity
        elif direction == UP:
            self.position += self.up * velocity
        elif direction == DOWN:
            self.position -= self.up * velocity

    #******************************************************************
    # Mouse look (mirrors Camera::ProcessMouseMovement)
    #******************************************************************

    def process_mouse_movement(self, 
                               x_offset: float, 
                               y_offset: float,
                               constrain_pitch= True):
        '''
        Rotate the camera based on mouse cursor delta values.

        The x_offset rotates yaw (left/right) and y_offset rotates
        pitch (up/down). Pitch is optionally clamped to +-89 degrees so the camera
        cannot flip upside down, matching the constrainPitch logic in camera.h

        ARGS:
        x_offset.........horizontal cursor delta in pixels (positive = right).
        y_offset.........vertical cursor delta in pixels (positive = up).
        constrain_pitch..if true, clamp pitch to +-89 degrees.
        '''

        self.yaw   += x_offset * self.mouse_sensitivity
        self.pitch += y_offset * self.mouse_sensitivity

        if constrain_pitch:
            self.pitch = max(-89.0, min(89.0, self.pitch))

        self._update_camera_vectors()

    #******************************************************************
    # Scroll wheel (mirrors Camera::ProcessMouseScroll())
    #******************************************************************

    def process_mouse_scroll(self, y_offset: float):
        '''
        Adjust camera movement speed via scroll wheen input.

        In the original C++ code, scroll adjusts MovementSpeed directly.
        ViewManager::Mouse_Scroll_Callback() clamps the final value to
        [0.5, 20.0]; that clamping is handled in ViewManager (Python Port).

        ARGS:
        y_offset.........vertical cursor delta in pixels (positive = up).
        '''

        self.movement_speed -= y_offset
        self.movement_speed  = max(0.1, min(45.0, self.movement_speed))

    #******************************************************************
    # PRIVATE HELPERS
    #******************************************************************

    def _update_camera_vectors(self):
        '''
        Recompute front, right, and up vectors from current yaw and pitch.

        Mirrors Camera::updateCameraVectors() in camera.h.
        Uses standard spherical-to-Cartesian conversion with Euler angles.
        '''
        yaw_rad    = math.radians(self.yaw)
        pitch_rad  = math.radians(self.pitch)

        #Compute the new front vector
        front = np.array([
            math.cos(yaw_rad) * math.cos(pitch_rad),
            math.sin(pitch_rad),
            math.sin(yaw_rad) * math.cos(pitch_rad),
        ], dtype=np.float32)
        self.front = front / np.linalg.norm(front) # normalize

        # derive right and up from the updated front and world_up
        self.right = np.cross(self.front, self.world_up)
        self.right /= np.linalg.norm(self.right)

        self.up = np.cross(self.right, self.front)
        self.up /= np.linalg.norm(self.up)