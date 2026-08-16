extends Label


func _process(_delta: float) -> void:
	text = "move touches: %d @ %s\nlook touches: %d @ %s\nmove_vec: %s\nviewport: %s  screen: %s" % [
		MobileInput.debug_move_touches,
		MobileInput.debug_last_move_touch_pos,
		MobileInput.debug_look_touches,
		MobileInput.debug_last_look_touch_pos,
		MobileInput.move_vector,
		get_viewport().size,
		DisplayServer.screen_get_size(),
	]
