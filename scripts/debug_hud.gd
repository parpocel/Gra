extends Label

var _raw_touch_count: int = 0
var _raw_drag_count: int = 0
var _raw_cancel_or_other: int = 0


func _input(event: InputEvent) -> void:
	if event is InputEventScreenTouch:
		_raw_touch_count += 1
	elif event is InputEventScreenDrag:
		_raw_drag_count += 1
	elif event is InputEventMouseButton or event is InputEventMouseMotion:
		_raw_cancel_or_other += 1


func _process(_delta: float) -> void:
	text = "RAW input -> touch:%d drag:%d mouse:%d\nmove: touches=%d drags=%d maxOff=%.1f @ %s\nlook: touches=%d drags=%d @ %s\nmove_vec: %s\nlast gui event: %s\nviewport: %s  screen: %s" % [
		_raw_touch_count,
		_raw_drag_count,
		_raw_cancel_or_other,
		MobileInput.debug_move_touches,
		MobileInput.debug_move_drags,
		MobileInput.debug_max_move_offset,
		MobileInput.debug_last_move_touch_pos,
		MobileInput.debug_look_touches,
		MobileInput.debug_look_drags,
		MobileInput.debug_last_look_touch_pos,
		MobileInput.move_vector,
		MobileInput.debug_last_event,
		get_viewport().size,
		DisplayServer.screen_get_size(),
	]
