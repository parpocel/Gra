extends Node

signal interact_pressed

var move_vector: Vector2 = Vector2.ZERO
var _look_delta: Vector2 = Vector2.ZERO

var debug_move_touches: int = 0
var debug_look_touches: int = 0
var debug_last_move_touch_pos: Vector2 = Vector2.ZERO
var debug_last_look_touch_pos: Vector2 = Vector2.ZERO
var debug_move_drags: int = 0
var debug_look_drags: int = 0
var debug_max_move_offset: float = 0.0
var debug_last_event: String = "none"


func set_move_vector(v: Vector2) -> void:
	move_vector = v


func add_look_delta(delta: Vector2) -> void:
	_look_delta += delta


func consume_look_delta() -> Vector2:
	var d := _look_delta
	_look_delta = Vector2.ZERO
	return d


func emit_interact() -> void:
	interact_pressed.emit()
