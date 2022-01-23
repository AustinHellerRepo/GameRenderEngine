from __future__ import annotations
import unittest
import time
from datetime import datetime, timedelta
import os
from typing import List, Dict, Set, Tuple, Callable, Type
import uuid
from src.austin_heller_repo.game_render_engine import RenderEngine, Model, ModelInstance, CameraInstance, Curve, Event, EventTypeEnum, MouseMovedEvent, AppendParallelCurvesInstanceDelta


def get_project_directory_path() -> str:
	return os.path.dirname(os.environ["VIRTUAL_ENV"])


__default_client_uuid = str(uuid.uuid4())
__king_model_uuid = str(uuid.uuid4())
__pawn_model_uuid = str(uuid.uuid4())
__camera_instance_uuid = str(uuid.uuid4())


def get_default_camera_instance_uuid() -> str:
	return __camera_instance_uuid


def get_default_render_engine(on_mouse_moved_callable: Callable[[RenderEngine, Event], None] = None, on_curve_completed_callable: Callable[[RenderEngine, Event], None] = None) -> RenderEngine:
	on_event_callable_per_event_type = {}
	if on_mouse_moved_callable is not None:
		on_event_callable_per_event_type[EventTypeEnum.MouseMoved] = on_mouse_moved_callable
	if on_curve_completed_callable is not None:
		on_event_callable_per_event_type[EventTypeEnum.CurveCompleted] = on_curve_completed_callable

	return RenderEngine(
		render_engine_uuid=__default_client_uuid,
		is_client=True,
		models=[
			Model(
				model_uuid=__king_model_uuid,
				model_file_path=os.path.join(get_project_directory_path(), "test/models/king")
			),
			Model(
				model_uuid=__pawn_model_uuid,
				model_file_path=os.path.join(get_project_directory_path(), "test/models/pawn")
			)
		],
		fonts=[],
		images=[],
		on_event_callable_per_event_type=on_event_callable_per_event_type,
		is_debug=True
	)


def get_default_client_uuid() -> str:
	return __default_client_uuid


def get_default_king_model_uuid() -> str:
	return __king_model_uuid


def get_default_pawn_model_uuid() -> str:
	return __pawn_model_uuid


class RenderEngineTest(unittest.TestCase):

	def test_initialize(self):

		print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: test_initialize: start")

		try:
			render_engine = get_default_render_engine()

			print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: test_initialize: created render_engine")

			self.assertIsNotNone(render_engine)

			print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: test_initialize: asserted render_engine")

			render_engine.start(
				on_start_callable=self.__test_initialize
			)

			print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: test_initialize: started render_engine")

			time.sleep(1.0)

			print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: test_initialize: end")

		except Exception as ex:
			print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: test_initialize: ex: {ex}")

		time.sleep(1.0)

	def __test_initialize(self, render_engine: RenderEngine):

		print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: __test_initialize: start")

		try:
			time.sleep(1.0)

			print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: __test_initialize: dispose: start")

			render_engine.dispose()

			print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: __test_initialize: dispose: end")

			time.sleep(1.0)

			print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: __test_initialize: end")
		except Exception as ex:
			print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: __test_initialize: ex: {ex}")

	def __dispose_render_engine_after_five_seconds(self, render_engine: RenderEngine):

		print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: __dispose_render_engine_after_five_seconds: start")

		time.sleep(5.0)

		print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: __dispose_render_engine_after_five_seconds: disposing")

		render_engine.dispose()

		print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: __dispose_render_engine_after_five_seconds: end")

	def test_model(self):
		# add a model instance to the render engine

		print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: test_model: start")

		render_engine = get_default_render_engine()

		render_engine.render_instances(
			instances=[
				ModelInstance(
					model_uuid=get_default_king_model_uuid(),
					instance_uuid=str(uuid.uuid4()),
					parallel_curves=[
						Curve(
							curve_uuid=str(uuid.uuid4()),
							position_deltas=[
								(0, 5, -1)
							],
							rotation_deltas=[],
							scale_deltas=[],
							opacity_deltas=[
								1.0
							],
							effective_time_seconds=5.0,
							is_controller_event_triggered_on_completed=False,
							start_datetime=datetime.utcnow(),
							is_instance_removed_on_curve_completed=False,
							restart_after_seconds=None
						)
					],
					client_event_types=[],
					renderer_event_types=[],
					owner_render_engine_uuid=render_engine.get_render_engine_uuid(),
					parent_instance_uuid=None
				)
			]
		)

		render_engine.start(
			on_start_callable=self.__dispose_render_engine_after_five_seconds
		)

		print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: test_model: end")

		time.sleep(1.0)

	def test_model_and_move_camera_forward(self):
		# add a model instance to the render engine and move the camera forward to it and stop

		print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: test_model_and_move_camera_forward: start")

		render_engine = get_default_render_engine()

		render_engine.render_instances(
			instances=[
				ModelInstance(
					model_uuid=get_default_king_model_uuid(),
					instance_uuid=str(uuid.uuid4()),
					parallel_curves=[
						Curve(
							curve_uuid=str(uuid.uuid4()),
							position_deltas=[
								(0, 5, -1)
							],
							rotation_deltas=[],
							scale_deltas=[],
							opacity_deltas=[
								1.0
							],
							effective_time_seconds=5.0,
							is_controller_event_triggered_on_completed=False,
							start_datetime=datetime.utcnow(),
							is_instance_removed_on_curve_completed=False,
							restart_after_seconds=None
						)
					],
					client_event_types=[],
					renderer_event_types=[],
					owner_render_engine_uuid=render_engine.get_render_engine_uuid(),
					parent_instance_uuid=None
				),
				CameraInstance(
					client_uuid=render_engine.get_render_engine_uuid(),
					instance_uuid=get_default_camera_instance_uuid(),
					parallel_curves=[
						Curve(
							curve_uuid=str(uuid.uuid4()),
							position_deltas=[
								(0, 1, 0),
								(0, 0.1, 0)
							],
							rotation_deltas=[],
							scale_deltas=[],
							opacity_deltas=[],
							effective_time_seconds=3.0,
							is_controller_event_triggered_on_completed=False,
							start_datetime=datetime.utcnow(),
							is_instance_removed_on_curve_completed=False,
							restart_after_seconds=None
						)
					],
					client_event_types=[],
					renderer_event_types=[],
					owner_render_engine_uuid=render_engine.get_render_engine_uuid(),
					parent_instance_uuid=None
				)
			]
		)

		render_engine.start(
			on_start_callable=self.__dispose_render_engine_after_five_seconds
		)

		print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: test_model_and_move_camera_forward: end")

	def test_model_and_move_camera_forward_twice(self):
		# add a model instance to the render engine and move forward twice at two different rates

		print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: test_model_and_move_camera_forward: start")

		render_engine = get_default_render_engine()

		render_engine.render_instances(
			instances=[
				ModelInstance(
					model_uuid=get_default_king_model_uuid(),
					instance_uuid=str(uuid.uuid4()),
					parallel_curves=[
						Curve(
							curve_uuid=str(uuid.uuid4()),
							position_deltas=[
								(0, 5, -1)
							],
							rotation_deltas=[],
							scale_deltas=[],
							opacity_deltas=[
								1.0
							],
							effective_time_seconds=5.0,
							is_controller_event_triggered_on_completed=False,
							start_datetime=datetime.utcnow(),
							is_instance_removed_on_curve_completed=False,
							restart_after_seconds=None
						)
					],
					client_event_types=[],
					renderer_event_types=[],
					owner_render_engine_uuid=render_engine.get_render_engine_uuid(),
					parent_instance_uuid=None
				),
				CameraInstance(
					client_uuid=render_engine.get_render_engine_uuid(),
					instance_uuid=get_default_camera_instance_uuid(),
					parallel_curves=[
						Curve(
							curve_uuid=str(uuid.uuid4()),
							position_deltas=[
								(0, 1, 0),
								(0, 1, 0),
								(0, 0, 0)
							],
							rotation_deltas=[],
							scale_deltas=[],
							opacity_deltas=[],
							effective_time_seconds=1.0,
							is_controller_event_triggered_on_completed=False,
							start_datetime=datetime.utcnow(),
							is_instance_removed_on_curve_completed=False,
							restart_after_seconds=None
						),
						Curve(
							curve_uuid=str(uuid.uuid4()),
							position_deltas=[
								(0, 0, 0),
								(0, 1, 0),
								(0, -0.5, 0)
							],
							rotation_deltas=[],
							scale_deltas=[],
							opacity_deltas=[],
							effective_time_seconds=4.0,
							is_controller_event_triggered_on_completed=False,
							start_datetime=datetime.utcnow() + timedelta(seconds=1.0),
							is_instance_removed_on_curve_completed=False,
							restart_after_seconds=None
						)
					],
					client_event_types=[],
					renderer_event_types=[],
					owner_render_engine_uuid=render_engine.get_render_engine_uuid(),
					parent_instance_uuid=None
				)
			]
		)

		render_engine.start(
			on_start_callable=self.__dispose_render_engine_after_five_seconds
		)

		print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: test_model_and_move_camera_forward: end")

	def test_model_and_move_camera_with_mouse(self):
		# add a model instance to the render engine and move the camera forward to it while allowing rotational movement with the mouse

		print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: test_model_and_move_camera_with_mouse: start")

		render_engine = get_default_render_engine(
			on_mouse_moved_callable=self.__test_model_and_move_camera_with_mouse_on_mouse_moved_callable
		)

		render_engine.render_instances(
			instances=[
				ModelInstance(
					model_uuid=get_default_king_model_uuid(),
					instance_uuid=str(uuid.uuid4()),
					parallel_curves=[
						Curve(
							curve_uuid=str(uuid.uuid4()),
							position_deltas=[
								(0, 5, -1)
							],
							rotation_deltas=[],
							scale_deltas=[],
							opacity_deltas=[
								1.0
							],
							effective_time_seconds=5.0,
							is_controller_event_triggered_on_completed=False,
							start_datetime=datetime.utcnow(),
							is_instance_removed_on_curve_completed=False,
							restart_after_seconds=None
						)
					],
					client_event_types=[],
					renderer_event_types=[],
					owner_render_engine_uuid=render_engine.get_render_engine_uuid(),
					parent_instance_uuid=None
				),
				CameraInstance(
					client_uuid=render_engine.get_render_engine_uuid(),
					instance_uuid=get_default_camera_instance_uuid(),
					parallel_curves=[
						Curve(
							curve_uuid=str(uuid.uuid4()),
							position_deltas=[
								(0, 1, 0),
								(0, 0.1, 0)
							],
							rotation_deltas=[],
							scale_deltas=[],
							opacity_deltas=[],
							effective_time_seconds=3.0,
							is_controller_event_triggered_on_completed=False,
							start_datetime=datetime.utcnow(),
							is_instance_removed_on_curve_completed=False,
							restart_after_seconds=None
						)
					],
					client_event_types=[],
					renderer_event_types=[],
					owner_render_engine_uuid=render_engine.get_render_engine_uuid(),
					parent_instance_uuid=None
				)
			]
		)

		render_engine.start(
			on_start_callable=self.__dispose_render_engine_after_five_seconds
		)

		print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: test_model_and_move_camera_with_mouse: end")

	def __test_model_and_move_camera_with_mouse_on_mouse_moved_callable(self, render_engine: RenderEngine, event: Event):
		if isinstance(event, MouseMovedEvent):
			render_engine.apply_instance_deltas(
				instance_deltas=[
					AppendParallelCurvesInstanceDelta(
						parallel_curves=[
							Curve(
								curve_uuid=str(uuid.uuid4()),
								position_deltas=[
									(event.get_mouse_x_delta(), event.get_mouse_y_delta(), 0)
								],
								rotation_deltas=[],
								scale_deltas=[],
								opacity_deltas=[],
								effective_time_seconds=event.get_time_delta(),
								is_controller_event_triggered_on_completed=False,
								start_datetime=event.get_triggered_datetime(),
								is_instance_removed_on_curve_completed=False,
								restart_after_seconds=False
							)
						],
						instance_delta_uuid=str(uuid.uuid4()),
						instance_uuid=get_default_camera_instance_uuid()
					)
				]
			)
