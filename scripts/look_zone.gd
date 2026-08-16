extends Control

var _touch_index: int = -1
var _last_pos: Vector2


func _gui_input(event: InputEvent) -> void:
	if event is InputEventScreenTouch:
		if event.pressed and _touch_index == -1:
			_touch_index = event.index
			_last_pos = event.position
			MobileInput.debug_look_touches += 1
			MobileInput.debug_last_look_touch_pos = event.position
		elif not event.pressed and event.index == _touch_index:
			_touch_index = -1
	elif event is InputEventScreenDrag and event.index == _touch_index:
		var delta: Vector2 = event.position - _last_pos
		_last_pos = event.position
		MobileInput.add_look_delta(delta)
