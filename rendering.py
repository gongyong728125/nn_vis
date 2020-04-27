import numpy as np
from OpenGL.GL import *

from opengl_helper.buffer import BufferObject
from opengl_helper.render_utility import VertexDataHandler, RenderSet, render_setting_0, render_setting_1
from opengl_helper.shader import RenderShaderHandler, RenderShader
from processing.edge_processing import EdgeProcessor
from processing.grid_processing import GridProcessor
from utility.performance import track_time
from utility.window import Window


class EdgeRenderer:
    def __init__(self, edge_handler: EdgeProcessor):
        self.edge_handler = edge_handler

        shader_handler = RenderShaderHandler()
        sample_point_shader: RenderShader = shader_handler.create("base", "sample/point.vert", "sample/point.frag")
        sample_sphere_shader: RenderShader = shader_handler.create("sample", "sample/ball_from_point.vert",
                                                                   "sample/ball_from_point.frag",
                                                                   "sample/ball_from_point.geom")
        sample_transparent_shader: RenderShader = shader_handler.create("trans", "sample/ball_from_point.vert",
                                                                        "sample/transparent_ball.frag",
                                                                        "sample/ball_from_point.geom")

        self.data_handler: VertexDataHandler = VertexDataHandler([(self.edge_handler.sample_buffer, 0)])

        self.point_render: RenderSet = RenderSet(sample_point_shader, self.data_handler)
        self.sphere_render: RenderSet = RenderSet(sample_sphere_shader, self.data_handler)
        self.transparent_render: RenderSet = RenderSet(sample_transparent_shader, self.data_handler)

    @track_time
    def render_point(self, window: Window, clear: bool = True, swap: bool = False):
        sampled_points: int = self.edge_handler.get_buffer_points()

        self.point_render.set_uniform_data([("projection", window.cam.projection, "mat4"),
                                            ("view", window.cam.get_view_matrix(), "mat4")])

        self.point_render.set()

        render_setting_0(clear)
        glPointSize(10.0)
        glDrawArrays(GL_POINTS, 0, sampled_points)
        if swap:
            window.swap()

    @track_time
    def render_sphere(self, window: Window, clear: bool = True, swap: bool = False):
        sampled_points: int = self.edge_handler.get_buffer_points()

        self.sphere_render.set_uniform_data([("projection", window.cam.projection, "mat4"),
                                             ("view", window.cam.get_view_matrix(), "mat4")])

        self.sphere_render.set()

        render_setting_0(clear)
        glDrawArrays(GL_POINTS, 0, sampled_points)
        if swap:
            window.swap()

    @track_time
    def render_transparent(self, window: Window, clear: bool = True, swap: bool = False):
        sampled_points: int = self.edge_handler.get_buffer_points()

        near, far = self.edge_handler.get_near_far_from_view()
        self.transparent_render.set_uniform_data([("projection", window.cam.projection, "mat4"),
                                                  ("view", window.cam.get_view_matrix(), "mat4"),
                                                  ("farthest_point_view_z", far, "float"),
                                                  ("nearest_point_view_z", near, "float")])

        self.transparent_render.set()

        render_setting_1(clear)
        glDrawArrays(GL_POINTS, 0, sampled_points)
        if swap:
            window.swap()


class GridRenderer:
    def __init__(self, grid_processor: GridProcessor):
        self.grid_processor = grid_processor

        shader_handler = RenderShaderHandler()
        point_shader: RenderShader = shader_handler.create("grid_base", "grid/point.vert", "grid/point.frag")
        cube_shader: RenderShader = shader_handler.create("grid_cube", "grid/cube.vert",
                                                          "grid/cube.frag",
                                                          "grid/cube.geom")

        self.grid_position_buffer: BufferObject = BufferObject()
        self.data_handler: VertexDataHandler = VertexDataHandler(
            [(self.grid_position_buffer, 0), (self.grid_processor.grid_density_buffer, 1)])

        self.point_render: RenderSet = RenderSet(point_shader, self.data_handler)
        self.cube_render: RenderSet = RenderSet(cube_shader, self.data_handler)

        self.set_grid_position_buffer_data()

    @track_time
    def set_grid_position_buffer_data(self):
        position_data = []
        print(self.grid_processor.grid_cell_count)
        for iz in range(self.grid_processor.grid_cell_count[2]):
            for iy in range(self.grid_processor.grid_cell_count[1]):
                for ix in range(self.grid_processor.grid_cell_count[0]):
                    position_data.append(
                        ix * self.grid_processor.grid_cell_size.x + self.grid_processor.bounding_volume[0].x)
                    position_data.append(
                        iy * self.grid_processor.grid_cell_size.y + self.grid_processor.bounding_volume[0].y)
                    position_data.append(
                        iz * self.grid_processor.grid_cell_size.z + self.grid_processor.bounding_volume[0].z)
                    position_data.append(1.0)

        transfer_data = np.array(position_data, dtype=np.float32)

        self.grid_position_buffer.load(transfer_data)

    @track_time
    def render_point(self, window: Window, clear: bool = True, swap: bool = False):
        grid_count: int = self.grid_processor.get_grid_count()

        self.point_render.set_uniform_data([("projection", window.cam.projection, "mat4"),
                                            ("view", window.cam.get_view_matrix(), "mat4")])

        self.point_render.set()

        render_setting_0(clear)
        glPointSize(10.0)
        glDrawArrays(GL_POINTS, 0, grid_count)
        if swap:
            window.swap()

    @track_time
    def render_cube(self, window: Window, clear: bool = True, swap: bool = False):
        grid_count: int = self.grid_processor.get_grid_count()

        self.cube_render.set_uniform_data([("projection", window.cam.projection, "mat4"),
                                           ("view", window.cam.get_view_matrix(), "mat4")])

        self.cube_render.set()

        render_setting_0(clear)
        glDrawArrays(GL_POINTS, 0, grid_count)
        if swap:
            window.swap()