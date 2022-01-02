from __future__ import annotations
import unittest
from typing import List, Tuple, Dict, Set, Type
import os
import sys
import time
from direct.showbase.ShowBase import ShowBase, DirectionalLight, LColor, PointLight, NodePath, CollisionBox, Point3F, CollisionNode, CollisionHandlerQueue, CollisionTraverser, CollisionHandlerPusher, CollisionEntry
from direct.task import Task
import math
from datetime import datetime
from austin_heller_repo.threading import start_thread


def get_project_directory_path() -> str:
	return os.path.dirname(os.environ["VIRTUAL_ENV"])


class Panda3dTest(unittest.TestCase):

	def test_helloworld(self):

		print(f"{datetime.utcnow()}: test: purpose: show empty window")

		class TestApp(ShowBase):

			def __init__(self):
				super().__init__()

				pass

		app = TestApp()

		with self.assertRaises(SystemExit):
			app.run()

		app.destroy()

	def test_model(self):

		print(f"{datetime.utcnow()}: test: purpose: show model that rotates around a point")

		class TestApp(ShowBase):

			def __init__(self):
				super().__init__()

				self.king_model = self.loader.loadModel(os.path.join(get_project_directory_path(), "test/models/king"))
				self.king_model.reparent_to(self.render)
				self.king_model.setPos(0, 5, 0)
				self.king_model.setHpr(90, 0, 0)

				directional_light = DirectionalLight("spotlight")
				self.light_source = self.render.attachNewNode(directional_light)
				self.render.setLight(self.light_source)

		def position_animation():
			print("thread: start")
			time.sleep(1)
			print("thread: active")
			angle = 0
			angle_delta = 0.01
			radius = 1
			center = app.king_model.getPos()
			cycles_total = 2
			rotations_total = 4
			while angle < cycles_total * math.pi * 2.0:
				try:
					x, y = math.cos(angle) * radius + center[0], math.sin(angle) * radius + center[1]
					cycle_angle = ((rotations_total / cycles_total) * angle) * (180 / math.pi)
					app.king_model.setPos(x, y, -1)
					app.king_model.setHpr(cycle_angle, 0, 0)
				except Exception as ex:
					print(f"ex: {ex}")
				angle += angle_delta
				time.sleep(0.01)
			print("thread: end")

		app = TestApp()

		thread = start_thread(position_animation)

		print(f"app.run: start")
		with self.assertRaises(SystemExit):
			app.run()
		print(f"app.run: end")

		app.destroy()

		print(f"thread.join: start")
		thread.join()
		print(f"thread.join: end")

	def test_change_model_halfway(self):

		print(f"{datetime.utcnow()}: test: purpose: show model that rotates around a point and then changes to a different model")
		# TODO change this to use instanceTo

		class TestApp(ShowBase):

			def __init__(self):
				super().__init__()

				self.active_model = None

				self.king_model = self.loader.loadModel(os.path.join(get_project_directory_path(), "test/models/king"))
				self.pawn_model = self.loader.loadModel(os.path.join(get_project_directory_path(), "test/models/pawn"))
				self.active_model = self.king_model

				self.active_model.reparent_to(self.render)
				self.active_model.setPos(0, 5, 0)
				self.active_model.setHpr(90, 0, 0)

				self.directional_light = DirectionalLight("directional_light")
				self.directional_light.color = (1, 0, 0, 1)
				self.directional_light_nodepath = self.render.attachNewNode(self.directional_light)
				self.render.setLight(self.directional_light_nodepath)

				self.point_light = PointLight("point_light")
				self.point_light.color = (0, 1, 0, 1)  # r, g, b, a
				self.point_light.attenuation = (0, 0, 1)  # constant, linear, quadratic
				self.point_light_nodepath = self.render.attachNewNode(self.point_light)
				self.point_light_nodepath.setPos(0, 5.5, 0)  # nodepath location
				self.render.setLight(self.point_light_nodepath)

				self.setBackgroundColor(0, 0, 0)

			def set_model(self, *, model):
				#self.render.removeNode(self.active_model)
				self.active_model.removeNode()
				self.active_model = model
				self.active_model.reparent_to(self.render)

		def position_animation():
			print("thread: start")
			time.sleep(1)
			print("thread: active")
			angle = 0
			angle_delta = 0.01
			radius = 1
			center = app.active_model.getPos()
			cycles_total = 2
			rotations_total = 4
			is_model_swapped = False
			while angle < cycles_total * math.pi * 2.0:
				try:
					x, y = math.cos(angle) * radius + center[0], math.sin(angle) * radius + center[1]
					cycle_angle = ((rotations_total / cycles_total) * angle) * (180 / math.pi)  # degrees (not radians)
					app.active_model.setPos(x, y, -1)
					app.active_model.setHpr(cycle_angle, 0, 0)
					app.directional_light.color = ((math.sin(angle) + 1) / 2.0, 0.5, (math.sin(angle + math.pi) + 1) / 2.0, 1)
					if not is_model_swapped and angle > cycles_total * math.pi:
						is_model_swapped = True
						app.set_model(
							model=app.pawn_model
						)
				except Exception as ex:
					print(f"ex: {ex}")
				angle += angle_delta
				time.sleep(0.01)
			print("thread: end")

		app = TestApp()

		thread = start_thread(position_animation)

		print(f"app.run: start")
		with self.assertRaises(SystemExit):
			app.run()
		print(f"app.run: end")

		app.destroy()

		print(f"thread.join: start")
		thread.join()
		print(f"thread.join: end")

		time.sleep(1)

	def test_velocity(self):

		print(f"{datetime.utcnow()}: test: purpose: show pawns that move together and then the second linear instance continues on")

		class TestApp(ShowBase):

			def __init__(self):
				super().__init__()

				self.__directional_light = DirectionalLight("directional_light")
				self.__directional_light.color = (1, 0, 0, 1)
				self.__directional_light_nodepath = self.render.attachNewNode(self.__directional_light)
				self.render.setLight(self.__directional_light_nodepath)

				self.__king_model = self.loader.loadModel(os.path.join(get_project_directory_path(), "test/models/king"))
				self.__king_model_instance = self.render.attachNewNode("king_model")
				self.__king_model.instanceTo(self.__king_model_instance)
				self.__king_model_instance.setPos(0, 5, -1)

				self.__pawn_model = self.loader.loadModel(os.path.join(get_project_directory_path(), "test/models/pawn"))
				self.__iterative_pawn_model_instance = self.render.attachNewNode("pawn_model")
				self.__pawn_model.instanceTo(self.__iterative_pawn_model_instance)
				self.__iterative_pawn_model_instance.setPos(1, 5, -1)
				self.__linear_pawn_model_instance = self.render.attachNewNode("pawn_model")
				self.__pawn_model.instanceTo(self.__linear_pawn_model_instance)
				self.__linear_pawn_model_instance.setPos(1, 5, -1)

				self.__pawn_velocity = -0.1
				self.__previous_time = 0

			def step_task(self, task: Task):
				if self.__previous_time == 0:
					print(task.time)
				time_delta, self.__previous_time = task.time - self.__previous_time, task.time

				position_delta = self.__pawn_velocity * time_delta

				position = self.__iterative_pawn_model_instance.getPos()
				if position[0] > -1:
					self.__iterative_pawn_model_instance.setPos(position[0] + position_delta, position[1], position[2])

				self.__linear_pawn_model_instance.setPos(1 + self.__pawn_velocity * self.__previous_time, position[1], position[2])

				if position[0] > -2:
					return task.cont

		app = TestApp()

		app.taskMgr.add(app.step_task, "step_task")

		print(f"{datetime.utcnow()}: test: app.run(): start")
		with self.assertRaises(SystemExit):
			app.run()
		print(f"{datetime.utcnow()}: test: app.run(): end")

	def test_collision_pusher(self):

		print(f"{datetime.utcnow()}: test: purpose: show pawn that collides with king and pushes it through/past the green light")

		class TestApp(ShowBase):

			def __init__(self):
				super().__init__()

				self.__directional_light = DirectionalLight("directional_light")
				self.__directional_light.color = (1, 0, 0, 1)
				self.__directional_light_nodepath = self.render.attachNewNode(self.__directional_light)
				self.render.setLight(self.__directional_light_nodepath)

				self.__king_model = self.loader.loadModel(os.path.join(get_project_directory_path(), "test/models/king"))
				self.__king_model_instance = self.render.attachNewNode("king_model")  # type: NodePath
				self.__king_model.instanceTo(self.__king_model_instance)
				self.__king_model_instance.setPos(0, 5, -1)
				self.__king_model_instance_collision_box = self.__king_model_instance.attachNewNode(CollisionNode("king_model_collision"))  # type: NodePath
				self.__king_model_instance_collision_box.node().addSolid(CollisionBox(Point3F(0, 0, 0.75), 0.25, 0.25, 0.75))
				self.__king_model_instance_collision_box.show()

				self.__pawn_model = self.loader.loadModel(os.path.join(get_project_directory_path(), "test/models/pawn"))
				self.__pawn_model_instance = self.render.attachNewNode("pawn_model")
				self.__pawn_model.instanceTo(self.__pawn_model_instance)
				self.__pawn_model_instance.setPos(1, 5, -1)
				self.__pawn_model_instance_collision_box = self.__pawn_model_instance.attachNewNode(CollisionNode("pawn_model_collision"))  # type: NodePath
				self.__pawn_model_instance_collision_box.node().addSolid(CollisionBox(Point3F(0, 0, 0.5), 0.25, 0.25, 0.5))
				self.__pawn_model_instance_collision_box.show()

				# NOTE this point light shows that the lighting is dynamic
				self.point_light = PointLight("point_light")
				self.point_light.color = (0, 1, 0, 1)  # r, g, b, a
				self.point_light.attenuation = (0, 0, 1)  # constant, linear, quadratic
				self.point_light_nodepath = self.render.attachNewNode(self.point_light)
				self.point_light_nodepath.setPos(-1.1, 5, 0)  # nodepath location
				self.render.setLight(self.point_light_nodepath)

				self.__pawn_velocity = -0.1
				self.__previous_time = 0

				self.cTrav = CollisionTraverser()
				self.__collision_handler = CollisionHandlerPusher()
				self.cTrav.addCollider(self.__king_model_instance_collision_box, self.__collision_handler)
				self.cTrav.showCollisions(self.render)

				# NOTE the pusher needs to know which NodePath must be pushed using the line below
				self.__collision_handler.addCollider(self.__king_model_instance_collision_box, self.__king_model_instance)

			def move_camera_task(self, task: Task):
				angle = task.time * 0.62
				radius = 4
				self.camera.setPos(math.sin(angle) * radius, -math.cos(angle) * radius + 5, 0)
				self.camera.setHpr(angle * (180/math.pi), 0, 0)

				return task.cont

			def step_task(self, task: Task):
				time_delta, self.__previous_time = task.time - self.__previous_time, task.time

				position_delta = self.__pawn_velocity * time_delta

				position = self.__pawn_model_instance.getPos()
				self.__pawn_model_instance.setPos(position[0] + position_delta, position[1], position[2])

				if position[0] > -1:
					return task.cont

		app = TestApp()

		app.taskMgr.add(app.step_task, "step_task")
		app.taskMgr.add(app.move_camera_task, "move_camera_task")

		print(f"{datetime.utcnow()}: test: app.run(): start")
		with self.assertRaises(SystemExit):
			app.run()
		print(f"{datetime.utcnow()}: test: app.run(): end")

	def test_collision_queue(self):

		print(f"{datetime.utcnow()}: test: purpose: show pawn that collides with king and prints when the events occur")

		class TestApp(ShowBase):

			def __init__(self):
				super().__init__()

				self.__directional_light = DirectionalLight("directional_light")
				self.__directional_light.color = (1, 0, 0, 1)
				self.__directional_light_nodepath = self.render.attachNewNode(self.__directional_light)
				self.render.setLight(self.__directional_light_nodepath)

				self.__king_model = self.loader.loadModel(os.path.join(get_project_directory_path(), "test/models/king"))
				self.__king_model_instance = self.render.attachNewNode("king_model")  # type: NodePath
				self.__king_model.instanceTo(self.__king_model_instance)
				self.__king_model_instance.setPos(0, 5, -1)
				self.__king_model_instance_collision_box = self.__king_model_instance.attachNewNode(CollisionNode("king_model_collision"))  # type: NodePath
				self.__king_model_instance_collision_box.node().addSolid(CollisionBox(Point3F(0, 0, 0.75), 0.25, 0.25, 0.75))
				self.__king_model_instance_collision_box.show()

				self.__pawn_model = self.loader.loadModel(os.path.join(get_project_directory_path(), "test/models/pawn"))
				self.__pawn_model_instance = self.render.attachNewNode("pawn_model")
				self.__pawn_model.instanceTo(self.__pawn_model_instance)
				self.__pawn_model_instance.setPos(1, 5, -1)
				self.__pawn_model_instance_collision_box = self.__pawn_model_instance.attachNewNode(CollisionNode("pawn_model_collision"))  # type: NodePath
				self.__pawn_model_instance_collision_box.node().addSolid(CollisionBox(Point3F(0, 0, 0.5), 0.25, 0.25, 0.5))
				self.__pawn_model_instance_collision_box.show()

				# NOTE this point light shows that the lighting is dynamic
				self.point_light = PointLight("point_light")
				self.point_light.color = (0, 1, 0, 1)  # r, g, b, a
				self.point_light.attenuation = (0, 0, 1)  # constant, linear, quadratic
				self.point_light_nodepath = self.render.attachNewNode(self.point_light)
				self.point_light_nodepath.setPos(-1.1, 5, 0)  # nodepath location
				self.render.setLight(self.point_light_nodepath)

				self.__pawn_velocity = -0.1
				self.__previous_time = 0

				self.cTrav = CollisionTraverser()
				self.__collision_handler = CollisionHandlerQueue()
				self.cTrav.addCollider(self.__king_model_instance_collision_box, self.__collision_handler)
				self.cTrav.showCollisions(self.render)

				# NOTE the pusher needs to know which NodePath must be pushed using the line below
				#self.__collision_handler.addCollider(self.__king_model_instance_collision_box, self.__king_model_instance)

			def move_camera_task(self, task: Task):
				angle = task.time * 0.62
				radius = 4
				self.camera.setPos(math.sin(angle) * radius, -math.cos(angle) * radius + 5, 0)
				self.camera.setHpr(angle * (180/math.pi), 0, 0)

				return task.cont

			def step_task(self, task: Task):
				time_delta, self.__previous_time = task.time - self.__previous_time, task.time

				position_delta = self.__pawn_velocity * time_delta

				position = self.__pawn_model_instance.getPos()
				self.__pawn_model_instance.setPos(position[0] + position_delta, position[1], position[2])

				if position[0] > -1:
					return task.cont

			def collision_detection_task(self, task: Task):
				entry: CollisionEntry
				for entry in self.__collision_handler.entries:
					print(entry)
					from_node_path = entry.getFromNodePath()
					print(f"from is king: {self.__king_model_instance is from_node_path}")
					print(f"from is pawn: {self.__pawn_model_instance is from_node_path}")
					print(f"type(from_node_path): {type(from_node_path)}")
					print(f"from is king_col: {self.__king_model_instance_collision_box is from_node_path}")
					print(f"from is pawn_col: {self.__pawn_model_instance_collision_box is from_node_path}")
					print(f"from eql king_col: {self.__king_model_instance_collision_box == from_node_path}")
					print(f"from eql pawn_col: {self.__pawn_model_instance_collision_box == from_node_path}")
					break
				else:
					return task.cont

		app = TestApp()

		app.taskMgr.add(app.step_task, "step_task")
		app.taskMgr.add(app.move_camera_task, "move_camera_task")
		app.taskMgr.add(app.collision_detection_task, "collision_detection_task")

		print(f"{datetime.utcnow()}: test: app.run(): start")
		with self.assertRaises(SystemExit):
			app.run()
		print(f"{datetime.utcnow()}: test: app.run(): end")

# TODO test collision and stop without colliding/merging into
