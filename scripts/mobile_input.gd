extends Node

signal interact_pressed

var move_vector: Vector2 = Vector2.ZERO
var _look_delta: Vector2 = Vector2.ZERO


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
