from __future__ import annotations
from typing import List, Tuple, Dict, Set, Callable, Type
from datetime import datetime
import uuid
from austin_heller_repo.common import StringEnum, FloatReference, DateTimeDeltaCalculator
from austin_heller_repo.threading import Semaphore
from abc import ABC, abstractmethod
import sys
import os
from direct.showbase.ShowBase import ShowBase, DirectionalLight, LColor, PointLight, NodePath, CollisionBox, Point3F, CollisionNode, CollisionHandlerQueue, CollisionTraverser, CollisionHandlerPusher, CollisionEntry, TextNode, TextFont, CardMaker, Texture, WindowProperties
from direct.task import Task
from direct.stdpy import threading


__cached_factorials = [
	1,
	1,
	2,
	6,
	24,
	120,
	720,
	5040,
	40320,
	362880,
	3628800,
	39916800
]


def get_cached_factorial(*, index: int) -> int:
	return __cached_factorials[index]


class EventTypeEnum(StringEnum):
	Collision = "collision"
	CurveCompleted = "curve_completed"
	Key = "key"
	MouseMoved = "mouse_moved"
	#ClientDisconnect = "client_disconnect"  # unable to source the event from within the render engine


class Event(ABC):

	def __init__(self, *, event_uuid: str, event_type: EventTypeEnum, source_render_engine_uuid: str, rendered_instance_states: List[RenderedInstanceState], triggered_datetime: datetime):

		self.__event_uuid = event_uuid
		self.__event_type = event_type
		self.__source_render_engine_uuid = source_render_engine_uuid
		self.__rendered_instance_states = rendered_instance_states
		self.__triggered_datetime = triggered_datetime

	def get_event_uuid(self) -> str:
		return self.__event_uuid

	def get_event_type(self) -> EventTypeEnum:
		return self.__event_type

	def get_source_render_engine_uuid(self) -> str:
		return self.__source_render_engine_uuid

	def get_rendered_instance_states(self) -> List[RenderedInstanceState]:
		return self.__rendered_instance_states

	def get_triggered_datetime(self) -> datetime:
		return self.__triggered_datetime

	def to_json(self) -> Dict:
		return {
			"event_uuid": self.__event_uuid,
			"event_type": self.__event_type.value,
			"source_render_engine_uuid": self.__source_render_engine_uuid,
			"rendered_instance_states": [x.to_json() for x in self.__rendered_instance_states],
			"triggered_datetime": self.__triggered_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")
		}

	@staticmethod
	def parse_json(*, json_dict: Dict) -> Event:
		event_type = EventTypeEnum(json_dict["event_type"])
		if event_type == EventTypeEnum.CurveCompleted:
			return CurveCompletedEvent.parse_json(
				json_dict=json_dict
			)
		elif event_type == EventTypeEnum.MouseMoved:
			return MouseMovedEvent.parse_json(
				json_dict=json_dict
			)
		elif event_type == EventTypeEnum.Collision:
			raise NotImplementedError()
		elif event_type == EventTypeEnum.Key:
			raise NotImplementedError()
		else:
			raise NotImplementedError()


class CurveCompletedEvent(Event):

	def __init__(self, *, curve_uuid: str, event_uuid: str, source_render_engine_uuid: str, rendered_instance_states: List[RenderedInstanceState], triggered_datetime: datetime):
		super().__init__(
			event_uuid=event_uuid,
			event_type=EventTypeEnum.CurveCompleted,
			source_render_engine_uuid=source_render_engine_uuid,
			rendered_instance_states=rendered_instance_states,
			triggered_datetime=triggered_datetime
		)

		self.__curve_uuid = curve_uuid

	def get_curve_uuid(self) -> str:
		return self.__curve_uuid

	def to_json(self) -> Dict:
		json_dict = super().to_json()
		json_dict["curve_uuid"] = self.__curve_uuid
		return json_dict

	@staticmethod
	def parse_json(*, json_dict: Dict) -> CurveCompletedEvent:
		return CurveCompletedEvent(
			curve_uuid=json_dict["curve_uuid"],
			event_uuid=json_dict["event_uuid"],
			source_render_engine_uuid=json_dict["source_render_engine_uuid"],
			rendered_instance_states=[RenderedInstanceState.parse_json(json_dict=x) for x in json_dict["rendered_instance_states"]],
			triggered_datetime=datetime.strptime(json_dict["triggered_datetime"], "%Y-%m-%d %H:%M:%S.%f")
		)


class MouseMovedEvent(Event):

	def __init__(self, *, mouse_x_delta: float, mouse_y_delta: float, time_delta: float, event_uuid: str, source_render_engine_uuid: str, rendered_instance_states: List[RenderedInstanceState], triggered_datetime: datetime):
		super().__init__(
			event_uuid=event_uuid,
			event_type=EventTypeEnum.MouseMoved,
			source_render_engine_uuid=source_render_engine_uuid,
			rendered_instance_states=rendered_instance_states,
			triggered_datetime=triggered_datetime
		)

		self.__mouse_x_delta = mouse_x_delta
		self.__mouse_y_delta = mouse_y_delta
		self.__time_delta = time_delta

	def get_mouse_x_delta(self) -> float:
		return self.__mouse_x_delta

	def get_mouse_y_delta(self) -> float:
		return self.__mouse_y_delta

	def get_time_delta(self) -> float:
		return self.__time_delta

	def to_json(self) -> Dict:
		json_dict = super().to_json()
		json_dict["mouse_x_delta"] = self.__mouse_x_delta
		json_dict["mouse_y_delta"] = self.__mouse_y_delta
		json_dict["time_delta"] = self.__time_delta
		return json_dict

	@staticmethod
	def parse_json(*, json_dict: Dict) -> MouseMovedEvent:
		return MouseMovedEvent(
			mouse_x_delta=json_dict["mouse_x_delta"],
			mouse_y_delta=json_dict["mouse_y_delta"],
			time_delta=json_dict["time_delta"],
			event_uuid=json_dict["event_uuid"],
			source_render_engine_uuid=json_dict["source_render_engine_uuid"],
			rendered_instance_states=[RenderedInstanceState.parse_json(json_dict=x) for x in json_dict["rendered_instance_states"]],
			triggered_datetime=datetime.strptime(json_dict["triggered_datetime"], "%Y-%m-%d %H:%M:%S.%f")
		)


class InstanceTypeEnum(StringEnum):
	Model = "model"
	Text = "text"
	Image = "image"
	Camera = "camera"


class Model():

	def __init__(self, *, model_uuid: str, model_file_path: str):

		self.__model_uuid = model_uuid
		self.__model_file_path = model_file_path

	def get_model_uuid(self) -> str:
		return self.__model_uuid

	def get_model_file_path(self) -> str:
		return self.__model_file_path


class Font():

	def __init__(self, *, font_uuid: str, font_file_path: str):

		self.__font_uuid = font_uuid
		self.__font_file_path = font_file_path

	def get_font_uuid(self) -> str:
		return self.__font_uuid

	def get_font_file_path(self) -> str:
		return self.__font_file_path


class Image():

	def __init__(self, *, image_uuid: str, image_file_path: str, image_size: Tuple[float, float]):

		self.__image_uuid = image_uuid
		self.__image_file_path = image_file_path
		self.__image_size = image_size

	def get_image_uuid(self) -> str:
		return self.__image_uuid

	def get_image_file_path(self) -> str:
		return self.__image_file_path

	def get_image_size(self) -> Tuple[float, float]:
		return self.__image_size


class Curve():

	def __init__(self, *, curve_uuid: str, position_deltas: List[Tuple[float, float, float]], rotation_deltas: List[Tuple[float, float, float]], scale_deltas: List[float], opacity_deltas: List[float], effective_time_seconds: float, is_controller_event_triggered_on_completed: bool, start_datetime: datetime, is_instance_removed_on_curve_completed: bool, restart_after_seconds: float):

		self.__curve_uuid = curve_uuid
		self.__position_deltas = position_deltas
		self.__rotation_deltas = rotation_deltas
		self.__scale_deltas = scale_deltas
		self.__opacity_deltas = opacity_deltas
		self.__effective_time_seconds = effective_time_seconds
		self.__is_controller_event_triggered_on_completed = is_controller_event_triggered_on_completed
		self.__start_datetime = start_datetime
		self.__is_instance_removed_on_curve_completed = is_instance_removed_on_curve_completed
		self.__restart_after_seconds = restart_after_seconds

	def get_curve_uuid(self) -> str:
		return self.__curve_uuid

	def get_position_deltas(self) -> List[Tuple[float, float, float]]:
		return self.__position_deltas

	def get_rotation_deltas(self) -> List[Tuple[float, float, float]]:
		return self.__rotation_deltas

	def get_scale_deltas(self) -> List[float]:
		return self.__scale_deltas

	def get_opacity_deltas(self) -> List[float]:
		return self.__opacity_deltas

	def get_effective_time_seconds(self) -> float:
		return self.__effective_time_seconds

	def get_is_controller_event_triggered_on_completed(self) -> bool:
		return self.__is_controller_event_triggered_on_completed

	def get_start_datetime(self) -> datetime:
		return self.__start_datetime

	def get_is_instance_removed_on_curve_completed(self) -> bool:
		return self.__is_instance_removed_on_curve_completed

	def get_restart_after_seconds(self) -> float:
		return self.__restart_after_seconds

	def to_json(self) -> Dict:
		return {
			"curve_uuid": self.__curve_uuid,
			"position_deltas": self.__position_deltas,
			"rotation_deltas": self.__rotation_deltas,
			"scale_deltas": self.__scale_deltas,
			"opacity_deltas": self.__opacity_deltas,
			"effective_time_seconds": self.__effective_time_seconds,
			"is_controller_event_triggered_on_completed": self.__is_controller_event_triggered_on_completed,
			"start_datetime": self.__start_datetime.strftime("%Y-%m-%d %H:%M:%S.%f"),
			"is_instance_removed_on_curve_completed": self.__is_instance_removed_on_curve_completed,
			"restart_after_seconds": self.__restart_after_seconds
		}

	@staticmethod
	def parse_json(json_dict: Dict) -> Curve:
		return Curve(
			curve_uuid=json_dict["curve_uuid"],
			position_deltas=json_dict["position_deltas"],
			rotation_deltas=json_dict["rotation_deltas"],
			scale_deltas=json_dict["scale_deltas"],
			opacity_deltas=json_dict["opacity_deltas"],
			effective_time_seconds=json_dict["effective_time_seconds"],
			is_controller_event_triggered_on_completed=json_dict["is_controller_event_triggered_on_completed"],
			start_datetime=datetime.strptime(json_dict["start_datetime"], "%Y-%m-%d %H:%M:%S.%f"),
			is_instance_removed_on_curve_completed=json_dict["is_instance_removed_on_curve_completed"],
			restart_after_seconds=json_dict["restart_after_seconds"]
		)

	def __try_update_vector(self, *, time_delta: float, vector: List[float], default_vector: List[float], vector_deltas: List[Tuple[float, float, float]]) -> bool:
		is_default_vector_update_needed = (time_delta == self.__effective_time_seconds)
		vector_length = len(vector)
		current_time_delta = 1
		for vector_delta_index, vector_delta in enumerate(vector_deltas):
			factorial = get_cached_factorial(
				index=vector_delta_index
			)
			for vector_index in range(vector_length):
				current_vector_delta = (vector_delta[vector_index] * current_time_delta) / factorial
				vector[vector_index] += current_vector_delta
				if is_default_vector_update_needed:
					default_vector[vector_index] += current_vector_delta
			current_time_delta *= time_delta
		return is_default_vector_update_needed

	def __try_update_float_reference(self, *, time_delta: float, float_reference: FloatReference, default_float_reference: FloatReference, float_reference_deltas: List[float]) -> bool:
		is_default_float_reference_update_needed = (time_delta == self.__effective_time_seconds)
		current_time_delta = 1
		for float_reference_delta_index, float_reference_delta in enumerate(float_reference_deltas):
			factorial = get_cached_factorial(
				index=float_reference_delta_index
			)
			current_float_reference_delta = (float_reference_delta * current_time_delta) / factorial
			float_reference.set(
				value=float_reference.get() + current_float_reference_delta
			)
			if is_default_float_reference_update_needed:
				default_float_reference.set(
					value=default_float_reference.get() + current_float_reference_delta
				)
			current_time_delta *= time_delta
		return is_default_float_reference_update_needed

	def try_update_position(self, *, time_delta: float, position: List[float], default_position: List[float]) -> bool:
		return self.__try_update_vector(
			time_delta=time_delta,
			vector=position,
			default_vector=default_position,
			vector_deltas=self.__position_deltas
		)

	def try_update_rotation(self, *, time_delta: float, rotation: List[float], default_rotation: List[float]) -> bool:
		return self.__try_update_vector(
			time_delta=time_delta,
			vector=rotation,
			default_vector=default_rotation,
			vector_deltas=self.__rotation_deltas
		)

	def try_update_scale(self, *, time_delta: float, scale: FloatReference, default_scale: FloatReference):
		return self.__try_update_float_reference(
			time_delta=time_delta,
			float_reference=scale,
			default_float_reference=default_scale,
			float_reference_deltas=self.__scale_deltas
		)

	def try_update_opacity(self, *, time_delta: float, opacity: FloatReference, default_opacity: FloatReference):
		return self.__try_update_float_reference(
			time_delta=time_delta,
			float_reference=opacity,
			default_float_reference=default_opacity,
			float_reference_deltas=self.__opacity_deltas
		)


class Instance(ABC):

	def __init__(self, *, instance_uuid: str, instance_type: InstanceTypeEnum, parallel_curves: List[Curve], client_event_types: List[EventTypeEnum], renderer_event_types: List[EventTypeEnum], owner_render_engine_uuid: str, parent_instance_uuid: str):

		self.__instance_uuid = instance_uuid
		self.__instance_type = instance_type
		self.__parallel_curves = parallel_curves
		self.__client_event_types = client_event_types
		self.__renderer_event_types = renderer_event_types
		self.__owner_render_engine_uuid = owner_render_engine_uuid
		self.__parent_instance_uuid = parent_instance_uuid

	def get_instance_uuid(self) -> str:
		return self.__instance_uuid

	def get_parallel_curves(self) -> List[Curve]:
		return self.__parallel_curves

	def set_parallel_curves(self, *, parallel_curves: List[Curve]):
		self.__parallel_curves = parallel_curves

	def remove_parallel_curve(self, *, parallel_curve: Curve):
		self.__parallel_curves.remove(parallel_curve)

	def get_client_event_types(self) -> List[EventTypeEnum]:
		return self.__client_event_types

	def get_renderer_event_types(self) -> List[EventTypeEnum]:
		return self.__renderer_event_types

	def get_owner_render_engine_uuid(self) -> str:
		return self.__owner_render_engine_uuid

	def set_owner_render_engine_uuid(self, *, owner_render_engine_uuid: str):
		self.__owner_render_engine_uuid = owner_render_engine_uuid

	def get_parent_instance_uuid(self) -> str:
		return self.__parent_instance_uuid

	def to_json(self) -> Dict:
		return {
			"instance_uuid": self.__instance_uuid,
			"instance_type": self.__instance_type.value,
			"parallel_curves": [x.to_json() for x in self.__parallel_curves],
			"client_event_types": [x.value for x in self.__client_event_types],
			"renderer_event_types": [x.value for x in self.__renderer_event_types],
			"owner_render_engine_uuid": self.__owner_render_engine_uuid,
			"parent_instance_uuid": self.__parent_instance_uuid
		}

	@staticmethod
	def parse_json(json_dict: Dict) -> Instance:
		instance_type = InstanceTypeEnum(json_dict["instance_type"])
		if instance_type == InstanceTypeEnum.Model:
			return ModelInstance.parse_json(
				json_dict=json_dict
			)
		elif instance_type == InstanceTypeEnum.Text:
			return TextInstance.parse_json(
				json_dict=json_dict
			)
		elif instance_type == InstanceTypeEnum.Image:
			return ImageInstance.parse_json(
				json_dict=json_dict
			)
		elif instance_type == InstanceTypeEnum.Camera:
			return CameraInstance.parse_json(
				json_dict=json_dict
			)
		else:
			raise NotImplementedError()


class ModelInstance(Instance):

	def __init__(self, model_uuid: str, instance_uuid: str, parallel_curves: List[Curve], client_event_types: List[EventTypeEnum], renderer_event_types: List[EventTypeEnum], owner_render_engine_uuid: str, parent_instance_uuid: str):
		super().__init__(
			instance_uuid=instance_uuid,
			instance_type=InstanceTypeEnum.Model,
			parallel_curves=parallel_curves,
			client_event_types=client_event_types,
			renderer_event_types=renderer_event_types,
			owner_render_engine_uuid=owner_render_engine_uuid,
			parent_instance_uuid=parent_instance_uuid
		)

		self.__model_uuid = model_uuid

	def get_model_uuid(self) -> str:
		return self.__model_uuid

	def to_json(self) -> Dict:
		json_dict = super().to_json()
		json_dict["model_uuid"] = self.__model_uuid
		return json_dict

	@staticmethod
	def parse_json(*, json_dict: Dict) -> ModelInstance:
		return ModelInstance(
			model_uuid=json_dict["model_uuid"],
			instance_uuid=json_dict["instance_uuid"],
			parallel_curves=[Curve.parse_json(x) for x in json_dict["parallel_curves"]],
			client_event_types=[EventTypeEnum(x) for x in json_dict["client_event_types"]],
			renderer_event_types=[EventTypeEnum(x) for x in json_dict["renderer_event_types"]],
			owner_render_engine_uuid=json_dict["owner_render_engine_uuid"],
			parent_instance_uuid=json_dict["parent_instance_uuid"]
		)


class TextInstance(Instance):

	def __init__(self, font_uuid: str, text: str, instance_uuid: str, parallel_curves: List[Curve], client_event_types: List[EventTypeEnum], renderer_event_types: List[EventTypeEnum], owner_render_engine_uuid: str, parent_instance_uuid: str):
		super().__init__(
			instance_uuid=instance_uuid,
			instance_type=InstanceTypeEnum.Text,
			parallel_curves=parallel_curves,
			client_event_types=client_event_types,
			renderer_event_types=renderer_event_types,
			owner_render_engine_uuid=owner_render_engine_uuid,
			parent_instance_uuid=parent_instance_uuid
		)

		self.__font_uuid = font_uuid
		self.__text = text

	def get_font_uuid(self) -> str:
		return self.__font_uuid

	def get_text(self) -> str:
		return self.__text

	def set_text(self, *, text: str):
		self.__text = text

	def to_json(self) -> Dict:
		json_dict = super().to_json()
		json_dict["font_uuid"] = self.__font_uuid
		json_dict["text"] = self.__text
		return json_dict

	@staticmethod
	def parse_json(*, json_dict: Dict) -> TextInstance:
		return TextInstance(
			font_uuid=json_dict["font_uuid"],
			text=json_dict["text"],
			instance_uuid=json_dict["instance_uuid"],
			parallel_curves=[Curve.parse_json(x) for x in json_dict["parallel_curves"]],
			client_event_types=[EventTypeEnum(x) for x in json_dict["client_event_types"]],
			renderer_event_types=[EventTypeEnum(x) for x in json_dict["renderer_event_types"]],
			owner_render_engine_uuid=json_dict["owner_render_engine_uuid"],
			parent_instance_uuid=json_dict["parent_instance_uuid"]
		)


class ImageInstance(Instance):

	def __init__(self, image_uuid: str, instance_uuid: str, parallel_curves: List[Curve], client_event_types: List[EventTypeEnum], renderer_event_types: List[EventTypeEnum], owner_render_engine_uuid: str, parent_instance_uuid: str):
		super().__init__(
			instance_uuid=instance_uuid,
			instance_type=InstanceTypeEnum.Image,
			parallel_curves=parallel_curves,
			client_event_types=client_event_types,
			renderer_event_types=renderer_event_types,
			owner_render_engine_uuid=owner_render_engine_uuid,
			parent_instance_uuid=parent_instance_uuid
		)

		self.__image_uuid = image_uuid

	def get_image_uuid(self) -> str:
		return self.__image_uuid

	def to_json(self) -> Dict:
		json_dict = super().to_json()
		json_dict["image_uuid"] = self.__image_uuid
		return json_dict

	@staticmethod
	def parse_json(*, json_dict: Dict) -> ImageInstance:
		return ImageInstance(
			image_uuid=json_dict["image_uuid"],
			instance_uuid=json_dict["instance_uuid"],
			parallel_curves=[Curve.parse_json(x) for x in json_dict["parallel_curves"]],
			client_event_types=[EventTypeEnum(x) for x in json_dict["client_event_types"]],
			renderer_event_types=[EventTypeEnum(x) for x in json_dict["renderer_event_types"]],
			owner_render_engine_uuid=json_dict["owner_render_engine_uuid"],
			parent_instance_uuid=json_dict["parent_instance_uuid"]
		)


class CameraInstance(Instance):

	def __init__(self, client_uuid: str, instance_uuid: str, parallel_curves: List[Curve], client_event_types: List[EventTypeEnum], renderer_event_types: List[EventTypeEnum], owner_render_engine_uuid: str, parent_instance_uuid: str):
		super().__init__(
			instance_uuid=instance_uuid,
			instance_type=InstanceTypeEnum.Camera,
			parallel_curves=parallel_curves,
			client_event_types=client_event_types,
			renderer_event_types=renderer_event_types,
			owner_render_engine_uuid=owner_render_engine_uuid,
			parent_instance_uuid=parent_instance_uuid
		)

		self.__client_uuid = client_uuid

	def get_client_uuid(self) -> str:
		return self.__client_uuid

	def to_json(self) -> Dict:
		json_dict = super().to_json()
		json_dict["client_uuid"] = self.__client_uuid
		return json_dict

	@staticmethod
	def parse_json(*, json_dict: Dict) -> CameraInstance:
		return CameraInstance(
			client_uuid=json_dict["client_uuid"],
			instance_uuid=json_dict["instance_uuid"],
			parallel_curves=[Curve.parse_json(x) for x in json_dict["parallel_curves"]],
			client_event_types=[EventTypeEnum(x) for x in json_dict["client_event_types"]],
			renderer_event_types=[EventTypeEnum(x) for x in json_dict["renderer_event_types"]],
			owner_render_engine_uuid=json_dict["owner_render_engine_uuid"],
			parent_instance_uuid=json_dict["parent_instance_uuid"]
		)


class InstanceDeltaTypeEnum(StringEnum):
	AppendParallelCurves = "append_parallel_curves"
	SetParallelCurves = "set_parallel_curves"
	SetText = "set_text"


class InstanceDelta(ABC):

	def __init__(self, *, instance_delta_uuid: str, instance_delta_type: InstanceDeltaTypeEnum, instance_uuid: str):

		self.__instance_delta_uuid = instance_delta_uuid
		self.__instance_delta_type = instance_delta_type
		self.__instance_uuid = instance_uuid

	def get_instance_delta_uuid(self) -> str:
		return self.__instance_delta_uuid

	def get_instance_delta_type(self) -> InstanceDeltaTypeEnum:
		return self.__instance_delta_type

	def get_instance_uuid(self) -> str:
		return self.__instance_uuid

	def to_json(self) -> Dict:
		return {
			"instance_delta_uuid": self.__instance_delta_uuid,
			"instance_delta_type": self.__instance_delta_type.value,
			"instance_uuid": self.__instance_uuid
		}

	@staticmethod
	def parse_json(*, json_dict: Dict) -> InstanceDelta:
		instance_delta_type = InstanceDeltaTypeEnum(json_dict["instance_delta_type"])
		if instance_delta_type == InstanceDeltaTypeEnum.AppendParallelCurves:
			return AppendParallelCurvesInstanceDelta.parse_json(
				json_dict=json_dict
			)
		elif instance_delta_type == InstanceDeltaTypeEnum.SetParallelCurves:
			return SetParallelCurvesInstanceDelta.parse_json(
				json_dict=json_dict
			)
		elif instance_delta_type == InstanceDeltaTypeEnum.SetText:
			return SetTextInstanceDelta.parse_json(
				json_dict=json_dict
			)
		else:
			raise NotImplementedError()

	@abstractmethod
	def apply_to_instance(self, *, instance: Instance):
		raise NotImplementedError()


class AppendParallelCurvesInstanceDelta(InstanceDelta):

	def __init__(self, *, parallel_curves: List[Curve], instance_delta_uuid: str, instance_uuid: str):
		super().__init__(
			instance_delta_uuid=instance_delta_uuid,
			instance_delta_type=InstanceDeltaTypeEnum.AppendParallelCurves,
			instance_uuid=instance_uuid
		)

		self.__parallel_curves = parallel_curves

	def apply_to_instance(self, *, instance: Instance):
		instance.set_parallel_curves(
			parallel_curves=instance.get_parallel_curves() + self.__parallel_curves
		)


class SetParallelCurvesInstanceDelta(InstanceDelta):

	def __init__(self, *, parallel_curves: List[Curve], instance_delta_uuid: str, instance_uuid: str):
		super().__init__(
			instance_delta_uuid=instance_delta_uuid,
			instance_delta_type=InstanceDeltaTypeEnum.SetParallelCurves,
			instance_uuid=instance_uuid
		)

		self.__parallel_curves = parallel_curves

	def apply_to_instance(self, *, instance: Instance):
		instance.set_parallel_curves(
			parallel_curves=self.__parallel_curves
		)


class SetTextInstanceDelta(InstanceDelta):

	def __init__(self, *, text: str, instance_delta_uuid: str, instance_uuid: str):
		super().__init__(
			instance_delta_uuid=instance_delta_uuid,
			instance_delta_type=InstanceDeltaTypeEnum.SetText,
			instance_uuid=instance_uuid
		)

		self.__text = text

	def get_text(self) -> str:
		return self.__text

	def apply_to_instance(self, *, instance: Instance):
		if isinstance(instance, TextInstance):
			instance.set_text(
				text=self.__text
			)
		else:
			raise NotImplementedError()


class RenderedInstanceState():

	def __init__(self, *, instance: Instance, position: Tuple[float, float, float], rotation: Tuple[float, float, float], scale: float, opacity: float):

		self.__instance = instance
		self.__position = position
		self.__rotation = rotation
		self.__scale = scale
		self.__opacity = opacity

	def get_instance(self) -> Instance:
		return self.__instance

	def get_position(self) -> Tuple[float, float, float]:
		return self.__position

	def get_rotation(self) -> Tuple[float, float, float]:
		return self.__rotation

	def get_scale(self) -> float:
		return self.__scale

	def get_opacity(self) -> float:
		return self.__opacity

	def to_json(self) -> Dict:
		return {
			"instance": self.__instance.to_json(),
			"position": self.__position,
			"rotation": self.__rotation,
			"scale": self.__scale,
			"opacity": self.__opacity
		}

	@staticmethod
	def parse_json(*, json_dict: Dict) -> RenderedInstanceState:
		return RenderedInstanceState(
			instance=Instance.parse_json(
				json_dict=json_dict["instance"]
			),
			position=json_dict["position"],
			rotation=json_dict["rotation"],
			scale=json_dict["scale"],
			opacity=json_dict["opacity"]
		)


class RenderedInstance():

	def __init__(self, *, instance: Instance, node_path: NodePath):

		self.__instance = instance
		self.__node_path = node_path

		self.__initial_position = [0, 0, 0]
		self.__position = [0, 0, 0]
		self.__initial_rotation = [0, 0, 0]
		self.__rotation = [0, 0, 0]
		self.__initial_scale = FloatReference(
			value=0
		)
		self.__scale = FloatReference(
			value=0
		)
		self.__initial_opacity = FloatReference(
			value=0
		)
		self.__opacity = FloatReference(
			value=0
		)
		self.__to_remove_parallel_curves = set()  # type: Set[Curve]
		self.__completed_curve_uuids = set()  # type: Set[str]
		self.__is_active_instance_removed_event = False

	def get_instance(self) -> Instance:
		return self.__instance

	def get_node_path(self) -> NodePath:
		return self.__node_path

	def pop_completed_curve_uuids(self) -> Set[str]:
		if self.__completed_curve_uuids:
			completed_curve_uuids = self.__completed_curve_uuids.copy()
			self.__completed_curve_uuids.clear()
			return completed_curve_uuids
		return set()

	def pop_is_active_instance_removed_event(self) -> bool:
		if self.__is_active_instance_removed_event:
			self.__is_active_instance_removed_event = False
			return True
		return False

	def update(self, *, time_delta: float, utc_now: datetime):

		self.__position[0] = self.__initial_position[0]
		self.__position[1] = self.__initial_position[1]
		self.__position[2] = self.__initial_position[2]

		for parallel_curve_index, parallel_curve in enumerate(self.__instance.get_parallel_curves()):
			start_datetime = parallel_curve.get_start_datetime()
			if start_datetime <= utc_now:
				effective_time_seconds = parallel_curve.get_effective_time_seconds()
				if effective_time_seconds == 0:
					self.__to_remove_parallel_curves.add(parallel_curve)
				else:
					calculated_time_delta = DateTimeDeltaCalculator.get_calculated_time_delta(
						start_datetime=parallel_curve.get_start_datetime(),
						effective_seconds=parallel_curve.get_effective_time_seconds(),
						now_datetime=utc_now,
						time_delta=time_delta
					)
					if calculated_time_delta > 0:
						if parallel_curve.try_update_position(
							time_delta=calculated_time_delta,
							position=self.__position,
							default_position=self.__initial_position
						):
							self.__to_remove_parallel_curves.add(parallel_curve)
							print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: update: finished processing parallel curve: self.__position: {self.__position}")
						parallel_curve.try_update_rotation(
							time_delta=calculated_time_delta,
							rotation=self.__rotation,
							default_rotation=self.__initial_rotation
						)
						parallel_curve.try_update_scale(
							time_delta=calculated_time_delta,
							scale=self.__scale,
							default_scale=self.__initial_scale
						)
						parallel_curve.try_update_opacity(
							time_delta=calculated_time_delta,
							opacity=self.__opacity,
							default_opacity=self.__initial_opacity
						)
						#print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: update: self.__position: {parallel_curve_index}: {self.__position}, {calculated_time_delta}")
		self.__node_path.setPos(self.__position[0], self.__position[1], self.__position[2])

		if self.__to_remove_parallel_curves:
			for parallel_curve in self.__to_remove_parallel_curves:
				self.__instance.remove_parallel_curve(
					parallel_curve=parallel_curve
				)
				if parallel_curve.get_is_controller_event_triggered_on_completed():
					self.__is_active_curve_completed_event = True
				if parallel_curve.get_is_instance_removed_on_curve_completed():
					self.__is_active_instance_removed_event = True

			self.__to_remove_parallel_curves.clear()

	def get_rendered_instance_state(self) -> RenderedInstanceState:
		return RenderedInstanceState(
			instance=self.__instance,
			position=self.__node_path.getPos(),
			rotation=self.__node_path.getHpr(),
			scale=self.__node_path.getScale(),
			opacity=self.__node_path.getColorScale()[3]
		)


class RenderShowBase(ShowBase):

	def __init__(self):
		super().__init__()

		# stop the mouse navigation default behavior
		self.disableMouse()


class RenderEngine():

	def __init__(self, *, render_engine_uuid: str, is_client: bool, models: List[Model], fonts: List[Font], images: List[Image], on_event_callable_per_event_type: Dict[EventTypeEnum, Callable[[RenderEngine, Event], None]], is_debug: bool = False):

		self.__render_engine_uuid = render_engine_uuid
		self.__is_client = is_client
		self.__models = models
		self.__fonts = fonts
		self.__images = images
		self.__on_event_callable_per_event_type = on_event_callable_per_event_type
		self.__is_debug = is_debug

		self.__found_exception = None  # type: Exception
		self.__instance_per_instance_uuid = {}  # type: Dict[str, Instance]
		self.__rendered_instance_per_instance_uuid = {}  # type: Dict[str, RenderedInstance]
		self.__rendered_instances_per_event_type = {}  # type: Dict[EventTypeEnum, Set[RenderedInstance]]
		self.__model_per_model_uuid = {}  # type: Dict[str, Model]
		self.__font_per_font_uuid = {}  # type: Dict[str, Font]
		self.__image_per_image_uuid = {}  # type: Dict[str, Image]
		self.__show_base = None  # type: ShowBase
		self.__model_node_path_per_model_uuid = {}  # type: Dict[str, NodePath]
		self.__text_font_per_font_uuid = {}  # type: Dict[str, TextFont]
		self.__texture_per_image_uuid = {}  # type: Dict[str, Texture]
		self.__on_start_thread = None  # type: threading.Thread
		self.__previous_time = 0
		self.__is_previous_time_dirty = False
		self.__previous_mouse_time = 0
		self.__previous_mouse_x = 0
		self.__previous_mouse_y = 0
		self.__to_remove_rendered_instance = set()  # type: Set[RenderedInstance]

		self.__initialize()

	def __initialize(self):
		if self.__is_debug:
			print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: __initialize: start")
		try:
			# cache the models, fonts, and images
			for model in self.__models:
				self.__model_per_model_uuid[model.get_model_uuid()] = model
			for font in self.__fonts:
				self.__font_per_font_uuid[font.get_font_uuid()] = font
			for image in self.__images:
				self.__image_per_image_uuid[image.get_image_uuid()] = image

			self.__show_base = RenderShowBase()

			for event_type in list(EventTypeEnum):
				self.__rendered_instances_per_event_type[event_type] = set()  # type: Set[RenderedInstance]

			if self.__is_client:
				self.__hide_mouse()
		finally:
			if self.__is_debug:
				print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: __initialize: end")

	def get_rendered_instance_states_by_event_type(self, *, event_type: EventTypeEnum) -> List[RenderedInstanceState]:
		rendered_instance_states = []  # type: List[RenderedInstanceState]
		for rendered_instance in self.__rendered_instances_per_event_type[event_type]:
			rendered_instance_states.append(rendered_instance.get_rendered_instance_state())
		return rendered_instance_states

	def __mouse_move_task(self, task: Task):
		if self.__show_base.mouseWatcherNode.hasMouse():
			mouse_x, mouse_y, triggered_datetime = self.__show_base.mouseWatcherNode.getMouseX(), self.__show_base.mouseWatcherNode.getMouseY(), datetime.utcnow()
			if self.__previous_mouse_x != mouse_x or self.__previous_mouse_y != mouse_y:
				mouse_x_delta = mouse_x - self.__previous_mouse_x
				mouse_y_delta = mouse_y - self.__previous_mouse_y
				time_delta = task.time - self.__previous_mouse_time
				self.__previous_mouse_x, self.__previous_mouse_y = mouse_x, mouse_y
				mouse_moved_event = MouseMovedEvent(
					mouse_x_delta=mouse_x_delta,
					mouse_y_delta=mouse_y_delta,
					time_delta=time_delta,
					event_uuid=str(uuid.uuid4()),
					source_render_engine_uuid=self.__render_engine_uuid,
					rendered_instance_states=self.get_rendered_instance_states_by_event_type(
						event_type=EventTypeEnum.MouseMoved
					),
					triggered_datetime=triggered_datetime
				)
				if EventTypeEnum.MouseMoved in self.__on_event_callable_per_event_type:
					self.__on_event_callable_per_event_type[EventTypeEnum.MouseMoved](self, mouse_moved_event)
		self.__previous_mouse_time = task.time
		return Task.cont

	def __hide_mouse(self):
		window_properties = WindowProperties()
		window_properties.setCursorHidden(True)
		window_properties.setMouseMode(WindowProperties.M_relative)
		self.__show_base.win.requestProperties(window_properties)

	def __show_mouse(self):
		window_properties = WindowProperties()
		window_properties.setCursorHidden(False)
		window_properties.setMouseMode(WindowProperties.M_absolute)
		self.__show_base.win.requestProperties(window_properties)

	def __render_instance_update_task(self, task: Task):
		#time_delta, self.__previous_time = task.time - self.__previous_time, task.time
		utc_now = datetime.utcnow()
		completed_curve_uuids = set()  # type: Set[str]
		for render_instance in self.__rendered_instance_per_instance_uuid.values():
			render_instance.update(
				time_delta=task.time + 1,
				utc_now=utc_now
			)
			completed_curve_uuids.update(render_instance.pop_completed_curve_uuids())
			if render_instance.pop_is_active_instance_removed_event():
				self.__to_remove_rendered_instance.add(render_instance)
				if self.__is_debug:
					print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: __render_instance_update_task: removing instance: {render_instance.get_instance().get_instance_uuid()}")
		if self.__to_remove_rendered_instance:
			for render_instance in self.__to_remove_rendered_instance:
				instance = render_instance.get_instance()
				instance_uuid = instance.get_instance_uuid()
				del self.__rendered_instance_per_instance_uuid[instance_uuid]
				del self.__instance_per_instance_uuid[instance_uuid]
				for event_type in instance.get_client_event_types() if self.__is_client else instance.get_renderer_event_types():
					self.__rendered_instances_per_event_type[event_type].remove(render_instance)
			self.__to_remove_rendered_instance.clear()
		if EventTypeEnum.CurveCompleted in self.__on_event_callable_per_event_type:
			if completed_curve_uuids:
				# trigger curve completed event
				rendered_instance_states = self.get_rendered_instance_states_by_event_type(
					event_type=EventTypeEnum.CurveCompleted
				)
				on_event_callable = self.__on_event_callable_per_event_type[EventTypeEnum.CurveCompleted]
				for completed_curve_uuid in completed_curve_uuids:
					curve_completed_event = CurveCompletedEvent(
						curve_uuid=completed_curve_uuid,
						event_uuid=str(uuid.uuid4()),
						source_render_engine_uuid=self.__render_engine_uuid,
						rendered_instance_states=rendered_instance_states,
						triggered_datetime=utc_now
					)
					on_event_callable(self, curve_completed_event)
		return Task.cont

	def get_render_engine_uuid(self) -> str:
		return self.__render_engine_uuid

	def start(self, on_start_callable: Callable[[RenderEngine], None]):
		if self.__is_debug:
			print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: start: start")
		try:
			def run():
				try:
					on_start_callable(self)
				except Exception as ex:
					if self.__found_exception is None:
						self.__found_exception = ex
			self.__on_start_thread = threading.Thread(
				target=run
			)
			if self.__is_debug:
				print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: start: starting on_start_callable thread")
			self.__on_start_thread.start()

			if self.__is_debug:
				print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: start: start render instance update task: start")
			self.__show_base.taskMgr.add(self.__render_instance_update_task)
			if self.__is_debug:
				print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: start: start render instance update task: end")

			if self.__is_debug:
				print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: start: start mouse move task: start")
			self.__show_base.taskMgr.add(self.__mouse_move_task)
			if self.__is_debug:
				print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: start: start mouse move task: end")

			try:
				if self.__is_debug:
					print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: start: running showbase: start")
				self.__show_base.run()
				if self.__is_debug:
					print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: start: running showbase: end")
			except SystemExit as ex:
				if self.__is_debug:
					print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: start: running showbase: system exit")
		finally:
			if self.__is_debug:
				print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: start: end")

	def render_instances(self, *, instances: List[Instance]):
		if self.__is_debug:
			print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: render_instances: start")
		try:
			for instance in instances:
				instance_uuid = instance.get_instance_uuid()
				self.__instance_per_instance_uuid[instance_uuid] = instance
				parent_node_path = None  # type: NodePath
				if instance.get_parent_instance_uuid() is None:
					parent_node_path = self.__show_base.render
				else:
					parent_node_path = self.__rendered_instance_per_instance_uuid[instance.get_parent_instance_uuid()].get_node_path()

				if isinstance(instance, ModelInstance):
					if self.__is_debug:
						print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: render_instances: found ModelInstance")
					model_uuid = instance.get_model_uuid()
					model = self.__model_per_model_uuid.get(model_uuid, None)
					if model is None:
						raise Exception(f"Failed to find model with model_uuid \"{model_uuid}\".")
					model_node_path = self.__model_node_path_per_model_uuid.get(model_uuid, None)
					if model_node_path is None:
						model_node_path = self.__show_base.loader.loadModel(model.get_model_file_path())
						self.__model_node_path_per_model_uuid[model_uuid] = model_node_path
					node_path = parent_node_path.attachNewNode(instance_uuid)
					model_node_path.instanceTo(node_path)
					# TODO determine if the scale and position should be set here instead of waiting for update step
				elif isinstance(instance, TextInstance):
					if self.__is_debug:
						print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: render_instances: found TextInstance")
					font_uuid = instance.get_font_uuid()
					font = self.__font_per_font_uuid.get(font_uuid, None)
					if font is None:
						raise Exception(f"Failed to find font with font_uuid: \"{font_uuid}\".")
					text_font = self.__text_font_per_font_uuid.get(font_uuid, None)
					if text_font is None:
						text_font = self.__show_base.loader.loadFont(font.get_font_file_path())
						self.__text_font_per_font_uuid[font_uuid] = text_font
					text_node = TextNode(instance_uuid)
					text_node.setFont(text_font)
					node_path = parent_node_path.attachNewNode(text_node)
				elif isinstance(instance, ImageInstance):
					if self.__is_debug:
						print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: render_instances: found ImageInstance")
					image_uuid = instance.get_image_uuid()
					image = self.__image_per_image_uuid.get(image_uuid, None)
					if image is None:
						raise Exception(f"Failed to find image with image_uuid: \"{image_uuid}\".")
					card_maker = CardMaker(instance_uuid)
					card_maker.setFrame(0, 0, image.get_image_size()[0], image.get_image_size()[1])
					node_path = parent_node_path.attachNewNode(card_maker.generate())  # type: NodePath
					texture = self.__texture_per_image_uuid.get(image_uuid, None)
					if texture is None:
						texture = self.__show_base.loader.loadTexture(image.get_image_file_path())
					node_path.setTexture(texture)
				elif isinstance(instance, CameraInstance):
					if self.__is_debug:
						print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: render_instances: found CameraInstance")
					node_path = None
					if self.__is_client:
						client_uuid = instance.get_client_uuid()
						if self.__render_engine_uuid == client_uuid:
							node_path = self.__show_base.camera
				else:
					if self.__is_debug:
						print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: render_instances: unexpected instance type: {type(instance)}")
					raise NotImplementedError()

				if node_path is not None:
					rendered_instance = RenderedInstance(
						instance=instance,
						node_path=node_path
					)
					self.__rendered_instance_per_instance_uuid[instance_uuid] = rendered_instance
					for event_type in instance.get_client_event_types() if self.__is_client else instance.get_renderer_event_types():
						self.__rendered_instances_per_event_type[event_type].add(rendered_instance)
		finally:
			if self.__is_debug:
				print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: render_instances: end")

	def apply_instance_deltas(self, *, instance_deltas: List[InstanceDelta]):
		if self.__is_debug:
			print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: apply_instance_deltas: start")
		try:
			for instance_delta in instance_deltas:
				instance_uuid = instance_delta.get_instance_uuid()
				instance = self.__instance_per_instance_uuid[instance_uuid]
				instance_delta.apply_to_instance(
					instance=instance
				)
		finally:
			if self.__is_debug:
				print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: apply_instance_deltas: end")

	def dispose(self):
		if self.__is_debug:
			print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: dispose: start")
		try:
			if self.__is_debug:
				print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: dispose: removing model nodes: start")
			for model_node_path in self.__model_node_path_per_model_uuid.values():
				model_node_path.removeNode()
			if self.__is_debug:
				print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: dispose: removing model nodes: end")

			if self.__is_debug:
				print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: dispose: releasing textures: start")
			for texture in self.__texture_per_image_uuid.values():
				texture.releaseAll()
			if self.__is_debug:
				print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: dispose: releasing textures: end")

			self.__show_base.shutdown()
			self.__show_base.destroy()

			def exitTask(task: Task):
				sys.exit()

			self.__show_base.taskMgr.add(exitTask)

			if self.__is_debug:
				print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: dispose: checking found exception: start")
			if self.__found_exception is not None:
				raise self.__found_exception
			if self.__is_debug:
				print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: dispose: checking found exception: end")
		finally:
			if self.__is_debug:
				print(f"{datetime.utcnow()}: {os.path.basename(__file__)}: dispose: end")


class RenderEngineFactory():

	def __init__(self, *, is_client: bool, models: List[Model], fonts: List[Font], images: List[Image], on_event_callable_per_event_type: Dict[EventTypeEnum, Callable[[RenderEngine, Event], None]] = None, is_debug: bool = False):

		self.__is_client = is_client
		self.__models = models
		self.__fonts = fonts
		self.__images = images
		self.__on_event_callable_per_event_type = on_event_callable_per_event_type
		self.__is_debug = is_debug

	def get_render_engine(self) -> RenderEngine:
		return RenderEngine(
			render_engine_uuid=str(uuid.uuid4()),
			is_client=self.__is_client,
			models=self.__models,
			fonts=self.__fonts,
			images=self.__images,
			on_event_callable_per_event_type=self.__on_event_callable_per_event_type,
			is_debug=self.__is_debug
		)
