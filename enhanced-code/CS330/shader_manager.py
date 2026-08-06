# *****CODE INFORMATION*****
# Name: Michael King
# Date: 7/17/2026
# File: shader_manager.py
# Assignment: CS-499 Enhancement 1
# CS-330 3D Scene Python Port
# University: SNHU
#
# Python port of ShaderManager.h/Shader.Manager.cpp from CS-330 (C++/OpenGL).
# ORIGINALLY MADE BY: Brian Battersby (SNHU Instructor).
# MODIFIED BY: Michael King
# Adapted for CS-499 Software Engineering Enhancement by Michael King
# PORTED TO PYTHON/PyOpenGL BY: Michael King
# 
# The ShaderManager class handles:
# 1. Loading GLSL vertex and fragment shader source files from disk
# 2. Compiling each shader stage and linking them into an OpenGL program
# 3. Exposing typed uniform-setter methods that mirror the inline helpers in
#    the original ShaderManager.h (setBoolValue, setIntValue, SetFloatValue,
#    setVec/2/3/4Value, setMat4Value, setSampler2DValue)
# 
# DESIGN NOTES:
# In C++ the setters were "inline" methods in the header. 
# In Python they are ordinary methods on the class, which is idiomatic and
# equally efficient at this scale. The uniform-location lookup is done lazily on
# each call, matching the original glGetUniformLocation usage pattern.

# ***Python Imports***
import ctypes
import numpy as np
from OpenGL.GL import (
    glCreateShader, glShaderSource, glCompileShader,
    glGetShaderiv, glGetShaderInfoLog,
    glCreateProgram, glAttachShader, glLinkProgram,
    glGetProgramiv, glGetProgramInfoLog,
    glDetachShader, glDeleteShader,
    glUseProgram, glGetUniformLocation,
    glUniform1i, glUniform1f,
    glUniform2f, glUniform3f, glUniform4f,
    glUniform2fv, glUniform3fv, glUniform4fv,
    glUniformMatrix4fv,
    GL_VERTEX_SHADER, GL_FRAGMENT_SHADER,
    GL_COMPILE_STATUS, GL_LINK_STATUS,
    GL_TRUE, GL_FALSE,
)

class ShaderManager:
    '''
    Manages a single OpenGL shader program.

    RESPONSIBILITIES (matching the original C++ class):
    1. Load and compile a vertex shader and a fragment shader from GLSL files
    2. Link them into a shader program
    3. Provide typed uniform setters used by ViewManager and SceneManager
    '''

    def __init__(self):
        '''Initialize with no program loaded yet.'''
        self.program_id: int=0 #OpenGL shader program handle; 0 = not loaded

    # *********************************************************
    # PROGRAM LOADING
    # *********************************************************

    def load_shaders(self, vertex_path: str, fragment_path: str) -> int:
        '''
        Load, compile and link a GLSL vertex shader and fragment shader

        Mirrors ShaderManager::LoadShaders() from ShaderManager.cpp.
        Prints compilation/link status to stdout, matching the original
        printf() diagnostic messages.

        ARGS:
        vertex_path......path to the .glsl vertex shader source file.
        fragment_path....path to the .glsl fragment shader source file.

        RETURNS:
        The linked OpenGL program ID, or 0 on failure.
        '''
        # *** read source files from disk ***
        try:
            with open(vertex_path, 'r') as f:
                vertex_src = f.read()
        except OSError:
            print(f"Cannot open {vertex_path}. Check your working directory.")
            return 0
        
        try:
            with open(fragment_path, 'r') as f:
                fragment_src = f.read()
        except OSError:
            print(f"Cannot open {fragment_path}. Check your working directory.")
            return 0

        # *** compile vertex shader***
        print(f"Compiling shader: {vertex_path}...", end="")
        vert_id=self._compile_shader(GL_VERTEX_SHADER, vertex_src)
        print("success")

        # *** compile fragment shader***
        print(f"Compiling shader: {fragment_path}...", end="")
        frag_id=self._compile_shader(GL_FRAGMENT_SHADER, fragment_src)
        print("success")

        # *** link program***
        print("Linking shader program...", end="")
        program_id = glCreateProgram()
        self.program_id = program_id
        glAttachShader(program_id, vert_id)
        glAttachShader(program_id, frag_id)
        glLinkProgram(program_id)

        # *** check link status ***
        if not glGetProgramiv(program_id, GL_LINK_STATUS):
            log = glGetProgramInfoLog(program_id)
            print(f"\nLink Error: {log.decode()}")
        else:
            print("success")

        # *** clean up individual shader objects now that they are linked
        glDetachShader(program_id, vert_id)
        glDetachShader(program_id, frag_id)
        glDeleteShader(vert_id)
        glDeleteShader(frag_id)

        return program_id
    
    def _compile_shader(self, shader_type: int, source: str) -> int:
        '''
        Compile a single GLSL shader stage and return its ID.

        ARGS:
        shader_type.......GL_VERTEX_SHADER or GL_FRAGMENT_SHADER.
        source............GLSL source code as a Python string.

        RETURNS:
        The compiled shader object ID.

        RAISES:
        RuntimeError: if the compilation fails, with the driver's info log.
        '''
        shader_id=glCreateShader(shader_type)
        glShaderSource(shader_id, source)
        glCompileShader(shader_id)

        if not glGetShaderiv(shader_id, GL_COMPILE_STATUS):
            log = glGetShaderInfoLog(shader_id)
            raise RuntimeError(f"Shader Compile Error:\n{log.decode()}")
        
        return shader_id
    
    # *********************************************************
    # PROGRAM ACTIVATION (mirrors ShaderManager::use())
    # *********************************************************

    def use(self):
        '''Activate this shader program for subsequent draw calls.'''
        glUseProgram(self.program_id)

    # *********************************************************
    # Uniform setters
    # mirror the inline methods in ShaderManager.h
    # *********************************************************

    def _loc(self, name: str) -> int:
        '''Return the uniform location for the given name in the active program'''
        return glGetUniformLocation(self.program_id, name)
    
    def set_bool(self, name: str, value: bool):
        '''Set a GLSL bool uniform (stored as int 0/1).'''
        glUniform1i(self._loc(name), int(value))

    def set_int(self, name: str, value: int):
        '''Set a GLSL int uniform.'''
        glUniform1i(self._loc(name), value)

    def set_float(self, name: str, value: float):
        '''Set a GLSL float uniform'''
        glUniform1f(self._loc(name), value)

    def set_vec2(self, name: str, x: float, y: float):
        '''Set a GLSL vec2 uniform from two scalar components.'''
        glUniform2f(self._loc(name), x, y)

    def set_vec3(self, name: str, x: float, y: float, z: float):
        '''Set a GLSL vec3 uniform from three scalar components.'''
        glUniform3f(self._loc(name), x, y, z)

    def set_vec4(self, name: str, x: float, y: float, z: float, w: float):
        '''Set a GLSL vec4 uniform from four scalar components.'''
        glUniform4f(self._loc(name), x, y, z, w)

    def set_mat4(self, name: str, matrix: np.ndarray):
        '''
        Upload a 4x4 matrix to a GLSL mat4 uniform.

        ARGS:
        name........Uniform name in the shader.
        matrix......A (4, 4) float32 numpy array in column-major (Fortran) order,
                    as produced by pyrr or glm-style matrix libraries.
                    GL_FALSE is passed so OpenGL does not transpose.
                    The caller is responsible for supplying the correct
                    layout.
        '''
        glUniformMatrix4fv(self._loc(name), 1, GL_FALSE, matrix)
    
    def set_sampler2d(self, name: str, slot: int):
        '''
        Bind a 2D texture sampler uniform to a texture unit slot.

        ARGS:
        name........Uniform name.
        slot........Texture unit index (0-15), matching the glActiveTexture slot
        '''
        glUniform1i(self._loc(name), slot)