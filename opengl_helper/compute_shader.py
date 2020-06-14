import math
import os
import time
from typing import Dict, Tuple, List

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from definitions import BASE_PATH
from opengl_helper.shader import BaseShader
from utility.singleton import Singleton
from opengl_helper.texture import Texture


class ComputeShader(BaseShader):
    def __init__(self, shader_src: str):
        BaseShader.__init__(self)
        self.shader_handle: int = compileProgram(compileShader(shader_src, GL_COMPUTE_SHADER))
        self.textures: List[Tuple[Texture, str, int]] = []
        self.uniform_cache: Dict[str, Tuple[int, any, any]] = dict()
        self.max_workgroup_size: int = glGetIntegeri_v(GL_MAX_COMPUTE_WORK_GROUP_COUNT, 0)[0]

    def compute(self, width: int, barrier: bool = False):
        for i in range(math.ceil(width / self.max_workgroup_size)):
            self.set_uniform_data(
                [('work_group_offset', i * self.max_workgroup_size, 'int')])

            for texture, flag, image_position in self.textures:
                texture.bind_as_image(flag, image_position)
            glUseProgram(self.shader_handle)

            for uniform_location, uniform_data, uniform_setter in self.uniform_cache.values():
                uniform_setter(uniform_location, uniform_data)

            if i == math.ceil(width / self.max_workgroup_size) - 1:
                glDispatchCompute(width % self.max_workgroup_size, 1, 1)
            else:
                glDispatchCompute(self.max_workgroup_size, 1, 1)
        if barrier:
            self.barrier()

    def barrier(self):
        glMemoryBarrier(GL_ALL_BARRIER_BITS)


class ComputeShaderHandler(metaclass=Singleton):
    def __init__(self):
        self.shader_dir: str = os.path.join(BASE_PATH, 'shader_src/compute')
        self.shader_list: Dict[str, ComputeShader] = dict()

    def create(self, shader_name: str, shader_file_path: str) -> ComputeShader:
        if shader_name in self.shader_list.keys():
            return self.shader_list[shader_name]
        shader_src = open(os.path.join(self.shader_dir, shader_file_path), 'r').read()
        self.shader_list[shader_name] = ComputeShader(shader_src)
        return self.shader_list[shader_name]

    def get(self, shader_name: str) -> ComputeShader:
        return self.shader_list[shader_name]
